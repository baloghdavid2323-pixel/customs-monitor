import os
import pandas as pd
from datetime import datetime

def generate_report(df: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = os.path.join(out_dir, f"report_{ts}.csv")
    html_path = os.path.join(out_dir, f"report_{ts}.html")
    df.to_csv(csv_path, index=False)
    html = df.to_html(index=False, escape=False)
    html_full = f"""
    <html><head><meta charset='utf-8'><title>Customs Monitor Report {ts}</title></head>
    <body>
    <h1>Customs Monitor Report – {ts}</h1>
    {html}
    </body></html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_full)
    return csv_path, html_path
