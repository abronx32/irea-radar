import json
from pathlib import Path
from datetime import datetime
from html import escape

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

cards = ""

for item in findings:
    url = item.get("content_url", "#") or "#"
    score = item.get("traffic_score", "")
    platform = item.get("platform", "")
    keyword = item.get("source_keyword", "")
    account = item.get("account", "")
    likes = item.get("likes", "")
    comments = item.get("comments", "")
    content_type = item.get("content_type", "")
    caption = item.get("observed_theme", "")

    if caption and len(caption) > 420:
        caption = caption[:420] + "..."

    cards += f"""
    <div class="card">
      <div class="topline">
        <span class="score">Score {escape(str(score))}</span>
        <span>{escape(str(platform))}</span>
        <span>{escape(str(content_type))}</span>
        <span>{escape(str(keyword))}</span>
      </div>

      <div class="metrics">
        <strong>Account:</strong> {escape(str(account or "—"))}
        &nbsp; | &nbsp;
        <strong>Likes:</strong> {escape(str(likes or "—"))}
        &nbsp; | &nbsp;
        <strong>Commenti:</strong> {escape(str(comments or "—"))}
      </div>

      <p class="caption">{escape(str(caption or ""))}</p>

      <a class="button" href="{escape(str(url))}" target="_blank">Apri contenuto</a>
    </div>
    """

if not findings:
    main_content = """
    <div class="empty">
      Nessun contenuto presente in <strong>data/findings.json</strong>.
    </div>
    """
else:
    main_content = cards

html = f"""
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <title>Irea Radar</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #f6f3ee;
      color: #1f1b16;
      padding: 28px;
      margin: 0;
    }}

    h1 {{
      margin: 0 0 6px 0;
      font-size: 34px;
    }}

    .subtitle {{
      color: #6f655b;
      margin-bottom: 24px;
    }}

    .card {{
      background: #ffffff;
      border: 1px solid #ded6ca;
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 16px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }}

    .topline {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .topline span {{
      background: #eee6da;
      padding: 6px 9px;
      border-radius: 999px;
      font-size: 13px;
    }}

    .topline .score {{
      background: #1f1b16;
      color: #ffffff;
      font-weight: bold;
    }}

    .metrics {{
      color: #4f463d;
      margin-bottom: 10px;
      font-size: 14px;
    }}

    .caption {{
      line-height: 1.45;
      color: #2b2621;
      margin-bottom: 14px;
    }}

    .button {{
      display: inline-block;
      background: #5f4632;
      color: #ffffff;
      text-decoration: none;
      padding: 9px 13px;
      border-radius: 8px;
      font-weight: bold;
      font-size: 14px;
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
    Report aggiornato: {datetime.now().strftime("%Y-%m-%d %H:%M")} · Contenuti trovati: {len(findings)}
  </div>

  {main_content}
</body>
</html>
"""

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report creato: {REPORT_FILE}")
