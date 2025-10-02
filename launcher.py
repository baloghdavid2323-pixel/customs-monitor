# launcher.py – fix útvonalas indító Windowsra (EXE-hez)
import subprocess, time
from pathlib import Path

# >>> Ha máshova tetted a projektet, EZZEL az útvonallal frissíts:
ROOT = Path(r"C:\Users\david\Downloads\customs_monitor")
VENV_PY = ROOT / r".venv\Scripts\python.exe"

# egyszerű log a hiba felderítéshez
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
def log(msg: str):
    with (LOG_DIR / "launcher.log").open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

if not VENV_PY.exists():
    log(f"[HIBA] Nem találom: {VENV_PY}")
    input("Nyomj Entert a kilépéshez...")
    raise SystemExit(1)

# secrets + data biztosítása
(ROOT / ".streamlit").mkdir(exist_ok=True)
sf = ROOT / ".streamlit" / "secrets.toml"
if not sf.exists():
    sf.write_text('database_url = "sqlite:///C:/Users/david/Downloads/customs_monitor/data/monitor.db"', encoding="utf-8")
(ROOT / "data").mkdir(exist_ok=True)

# Collector
cmd1 = f'start "Customs Monitor - Collector" cmd /k cd /d "{ROOT}" ^&^& "{VENV_PY}" -m src.main'
log(f"RUN: {cmd1}")
subprocess.Popen(cmd1, shell=True)

time.sleep(1)

# Dashboard
cmd2 = f'start "Customs Monitor - Dashboard" cmd /k cd /d "{ROOT}" ^&^& "{VENV_PY}" -m streamlit run dashboard/app.py'
log(f"RUN: {cmd2}")
subprocess.Popen(cmd2, shell=True)

log("Indítás kész – két ablaknak kell nyílnia (Collector, Dashboard).")
input("Nyomj Entert a kilépéshez...")
