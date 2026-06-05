import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "findings.json"
REPORT_DIR = ROOT / "reports"
REPORT_FILE = REPORT_DIR / "latest.html"

REPORT_DIR.mkdir(exist_ok=True)

if DATA_FILE.exists():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        findings = json.load(f)
else:
    findings = []

findings = sorted(
    findings,
    key=lambda x: x.get("traffic_score", 0) or 0,
    reverse=True
)

rows = ""

for item in findings:
    rows += f"""
    <tr>
      <td>{item.get("traffic_score", "")}</td>
      <td>{item.get("platform", "")}</td>
      <td>{item.get("source_keyword", "")}</td>
      <td>{item.get("title", "")}</td>
      <td>{item.get("views", "")}</td>
      <td>{item.get("likes", "")}</td>
      <td>{item.get("hook", "")}</td>
      <td>{item.get("copy_model", "")}</td>
      <td><a href="{item.get("content_url", "#")}" target="_blank">Apri</a></td>
    </tr>
    """

html = f"""
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Irea Radar</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #f6f3ee;
      color: #1f1b16;
      padding: 32px;
    }}

    h1 {{
      margin-bottom: 4px;
      font-size: 34px;
    }}

    .subtitle {{
      color: #6f655b;
      margin-bottom: 28px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
      font-size: 14px;
    }}

    th, td {{
      padding: 12px;
      border-bottom: 1px solid #ddd;
      vertical-align: top;
      text-align: left;
    }}

    th {{
      background: #e7dfd2;
      font-weight: bold;
    }}

    a {{
      color: #5f4632;
      font-weight: bold;
      text-decoration: none;
    }}

    .empty {{
      background: white;
      padding: 24px;
      border: 1px solid #ddd;
      max-width: 720px;
    }}
  </style>
</head>
<body>
  <h1>Irea Radar</h1>
  <div class="subtitle">
    Report aggiornato: {datetime.now().strftime("%Y-%m-%d %H:%M")}
  </div>

  {"""
  <div class="empty">
    Nessun contenuto ancora presente in <strong>data/findings.json</strong>.<br>
    Il radar è pronto: nel prossimo step aggiungeremo il collector.
  </div>
  """ if not findings else f"""
  <table>
    <thead>
      <tr>
        <th>Score</th>
        <th>Piattaforma</th>
        <th>Keyword</th>
        <th>Contenuto</th>
        <th>Views</th>
        <th>Likes</th>
        <th>Hook</th>
        <th>Modello da copiare</th>
        <th>Link</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  """}
</body>
</html>
"""

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report creato: {REPORT_FILE}")
