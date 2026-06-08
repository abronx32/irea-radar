import json
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]

KEYWORDS_FILE = ROOT / "data" / "keywords.txt"
FINDINGS_FILE = ROOT / "data" / "findings.json"

with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
    keywords = [
        line.strip()
        for line in f.readlines()
        if line.strip()
    ]

results = []

today = datetime.now().strftime("%Y-%m-%d")

for keyword in keywords:

    encoded = quote_plus(keyword)

    results.append({
        "date_found": today,
        "platform": "Instagram",
        "source_keyword": keyword,
        "content_url": f"https://www.instagram.com/explore/search/keyword/?q={encoded}",
        "account": "",
        "title": f"Instagram search: {keyword}",
        "views": None,
        "likes": None,
        "comments": None,
        "traffic_score": 0,
        "content_type": "search",
        "observed_theme": "",
        "hook": "",
        "visual_pattern": "",
        "audio_or_text_pattern": "",
        "why_it_gets_attention": "",
        "copy_model": "",
        "adaptation_potential_for_irea": "",
        "screenshot_url": ""
    })

    results.append({
        "date_found": today,
        "platform": "TikTok",
        "source_keyword": keyword,
        "content_url": f"https://www.tiktok.com/search?q={encoded}",
        "account": "",
        "title": f"TikTok search: {keyword}",
        "views": None,
        "likes": None,
        "comments": None,
        "traffic_score": 0,
        "content_type": "search",
        "observed_theme": "",
        "hook": "",
        "visual_pattern": "",
        "audio_or_text_pattern": "",
        "why_it_gets_attention": "",
        "copy_model": "",
        "adaptation_potential_for_irea": "",
        "screenshot_url": ""
    })

    results.append({
        "date_found": today,
        "platform": "Pinterest",
        "source_keyword": keyword,
        "content_url": f"https://www.pinterest.com/search/pins/?q={encoded}",
        "account": "",
        "title": f"Pinterest search: {keyword}",
        "views": None,
        "likes": None,
        "comments": None,
        "traffic_score": 0,
        "content_type": "search",
        "observed_theme": "",
        "hook": "",
        "visual_pattern": "",
        "audio_or_text_pattern": "",
        "why_it_gets_attention": "",
        "copy_model": "",
        "adaptation_potential_for_irea": "",
        "screenshot_url": ""
    })

with open(FINDINGS_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Creati {len(results)} risultati")
