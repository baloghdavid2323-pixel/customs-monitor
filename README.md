# Customs Monitor (Vám- és jogszabályfigyelő rendszer)

Teljes, futtatható mintaprojekt az EU vámkódex, vámszabályok és kapcsolódó jogi változások **automatikus figyelésére**, kockázat- és hatáselemzéssel, riporttal és dashboarddal.

## 🚀 Fő funkciók
- Források: EUR-Lex (RSS), Európai Bizottság Taxation & Customs (web), NAV (web)
- Szűrés kulcsszavak alapján (HU/EN)
- Nyelvfelismerés, egyszerű kockázat- és hatásbecslés
- SQLite adatbázis (alapértelmezés), SQLAlchemy ORM
- Időzített futás (APScheduler)
- Heti jelentés (CSV + HTML)
- Értesítések e-mailen és Slack-en (opcionális)
- Streamlit alapú dashboard

## 📦 Telepítés (lokális gépen)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Beállítás
Szerkeszd a `config.yaml` fájlt:
- időzítés (`fetch_interval_minutes`)
- értesítések (email/slack)
- kulcsszavak, források

## ▶️ Futtatás
```bash
export PYTHONPATH=.
python src/main.py
```
Az első futás létrehozza a `data/monitor.db` adatbázist, és elindítja az ütemezőt.

## 📈 Dashboard
Külön terminálban indítható:
```bash
streamlit run dashboard/app.py
```
A dashboard az `sqlite:///data/monitor.db` adatbázist használja (módosítható a `st.secrets`-ben).

## 📨 E-mail és Slack értesítés
- **E-mail**: állítsd be a `notifications.email` részt (pl. Gmail app password).
- **Slack**: add meg a bot tokent és a csatornát.

## 🔐 Megjegyzés
A mintakód általános HTML-strukturát feltételez a weboldalakon; szükség esetén **testre szabható** a szelektorok finomítása a `src/sources/*.py` fájlokban.

## 🗂 Projektstruktúra
```
customs_monitor/
  config.yaml
  requirements.txt
  src/
    main.py
    sources/{eurlex.py, taxud.py, nav.py}
    analyze/{nlp.py, risk.py}
    storage/db.py
    report/generate_report.py
    notify/{emailer.py, slack.py}
    utils/logging.py
  dashboard/app.py
  data/
```
