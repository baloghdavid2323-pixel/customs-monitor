import os
import yaml
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from src.utils.logging import setup_logging
from src.storage.db import get_session, Item, make_fingerprint
from src.analyze.nlp import detect_lang
from src.analyze.risk import score_item
from src.report.generate_report import generate_report
from src.notify.emailer import send_email
from src.notify.slack import send_slack

from src.sources import eurlex, taxud, nav

logger = setup_logging()

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_all(cfg):
    collected = []
    if cfg["sources"].get("eurlex", {}).get("enabled"):
        collected += eurlex.fetch(cfg["sources"]["eurlex"])
    if cfg["sources"].get("taxud", {}).get("enabled"):
        collected += taxud.fetch(cfg["sources"]["taxud"])
    if cfg["sources"].get("nav", {}).get("enabled"):
        collected += nav.fetch(cfg["sources"]["nav"])
    return collected

def persist_and_analyze(items, cfg):
    session = get_session(cfg["app"]["database_url"])
    new_rows = []
    for it in items:
        title = (it.get("title") or "").strip()
        url = it.get("url") or ""
        if not title or not url:
            continue
        fp = make_fingerprint(it["source"], title, url)
        exists = session.query(Item).filter_by(fingerprint=fp).first()
        if exists:
            continue
        text = " ".join([t for t in [title, it.get("summary"), it.get("content")] if t])
        lang = detect_lang(text) if text else None
        rules = {
            "high": cfg["analysis"]["risk_rules"]["high"],
            "medium": cfg["analysis"]["risk_rules"]["medium"],
            "low": cfg["analysis"]["risk_rules"]["low"],
            "impact_tags": cfg["analysis"]["impact_tags"]
        }
        risk, direct, indirect = score_item(text, rules)

        row = Item(
            source=it["source"],
            title=title,
            url=url,
            published_at=it.get("published_at"),
            summary=it.get("summary"),
            content=it.get("content"),
            lang=lang,
            risk_level=risk,
            impact_direct=direct,
            impact_indirect=indirect,
            processed=True,
            fingerprint=fp
        )
        session.add(row)
        session.commit()
        new_rows.append(row)
    return new_rows

def alert(new_rows, cfg):
    if not new_rows:
        return
    high = [r for r in new_rows if r.risk_level == "high"]
    if not high:
        return
    lines = ["Új, magas kockázatú változás észlelve:\n"]
    for r in high:
        lines.append(f"- {r.title} ({r.url})")
    msg = "\n".join(lines)

    if cfg["notifications"]["email"]["enabled"]:
        send_email(
            cfg["notifications"]["email"]["smtp_user"],
            cfg["notifications"]["email"]["smtp_password"],
            [cfg["notifications"]["email"]["smtp_user"]],
            f"{cfg['notifications']['email']['subject_prefix']} High risk alerts",
            msg
        )
    if cfg["notifications"]["slack"]["enabled"]:
        send_slack(
            cfg["notifications"]["slack"]["bot_token"],
            cfg["notifications"]["slack"]["channel"],
            msg
        )

def make_weekly_report(cfg):
    from sqlalchemy import create_engine, text
    engine = create_engine(cfg["app"]["database_url"], echo=False, future=True)
    with engine.connect() as con:
        df = pd.read_sql(text("""
            SELECT source, title, url, published_at, risk_level, impact_direct, impact_indirect, created_at
            FROM items
            WHERE created_at >= datetime('now', '-7 day')
            ORDER BY created_at DESC
        """), con)
    out_dir = cfg["reporting"]["out_dir"]
    csv_path, html_path = generate_report(df, out_dir)
    logger.info(f"Report generated: {csv_path}, {html_path}")

def job():
    cfg = load_config()
    items = fetch_all(cfg)
    logger.info(f"Fetched {len(items)} raw items")
    new_rows = persist_and_analyze(items, cfg)
    logger.info(f"Inserted {len(new_rows)} new items")
    alert(new_rows, cfg)

if __name__ == "__main__":
    cfg = load_config()
    os.makedirs("data/reports", exist_ok=True)
    job()

    scheduler = BlockingScheduler(timezone=cfg["app"]["timezone"])
    scheduler.add_job(job, "interval", minutes=cfg["app"]["fetch_interval_minutes"], id="fetch_job")
    scheduler.add_job(make_weekly_report, "cron",
                      day_of_week=cfg["reporting"]["weekly_day_of_week"],
                      hour=cfg["reporting"]["weekly_hour"],
                      args=[cfg],
                      id="weekly_report")
    logger.info("Scheduler started")
    scheduler.start()
