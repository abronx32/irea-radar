import json
import os
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS_FILE = ROOT / "data" / "keywords.txt"
FINDINGS_FILE = ROOT / "data" / "findings.json"

MAX_LINKS_PER_KEYWORD = 8


def keyword_to_hashtag(keyword: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9 ]", "", keyword.lower())
    return cleaned.replace(" ", "")


def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def make_item(keyword, url):
    today = datetime.now().strftime("%Y-%m-%d")

    content_type = "reel" if "/reel/" in url else "post"

    return {
        "date_found": today,
        "platform": "Instagram",
        "source_keyword": keyword,
        "content_url": url,
        "account": "",
        "title": f"Instagram {content_type}: {keyword}",
        "views": None,
        "likes": None,
        "comments": None,
        "traffic_score": 10 if content_type == "reel" else 5,
        "content_type": content_type,
        "observed_theme": "",
        "hook": "",
        "visual_pattern": "",
        "audio_or_text_pattern": "",
        "why_it_gets_attention": "",
        "copy_model": "",
        "adaptation_potential_for_irea": "",
        "screenshot_url": ""
    }


def instagram_login(page):
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        print("Instagram secrets non presenti. Provo senza login.")
        return False

    print("Provo login Instagram...")

    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    try:
        page.fill("input[name='username']", username, timeout=15000)
        page.fill("input[name='password']", password, timeout=15000)
        page.click("button[type='submit']", timeout=15000)
        page.wait_for_timeout(12000)

        current_url = page.url

        if "challenge" in current_url or "accounts/login" in current_url:
            print("Login non completato. Possibile verifica Instagram.")
            return False

        print("Login Instagram completato.")
        return True

    except PlaywrightTimeoutError:
        print("Timeout durante il login Instagram.")
        return False
    except Exception as e:
        print(f"Errore login Instagram: {e}")
        return False


def collect_instagram_links(page, keyword):
    hashtag = keyword_to_hashtag(keyword)
    hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"

    print(f"Cerco keyword: {keyword} → #{hashtag}")

    try:
        page.goto(hashtag_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)

        hrefs = page.eval_on_selector_all(
            "a[href]",
            "els => els.map(a => a.href)"
        )

        links = []

        for href in hrefs:
            if "/reel/" in href or "/p/" in href:
                clean = href.split("?")[0]
                if clean not in links:
                    links.append(clean)

        return links[:MAX_LINKS_PER_KEYWORD]

    except Exception as e:
        print(f"Errore su keyword {keyword}: {e}")
        return []


def main():
    keywords = load_keywords()
    findings = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        instagram_login(page)

        for keyword in keywords:
            links = collect_instagram_links(page, keyword)

            for url in links:
                if url not in seen_urls:
                    seen_urls.add(url)
                    findings.append(make_item(keyword, url))

        browser.close()

    with open(FINDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    print(f"Salvati {len(findings)} contenuti Instagram in {FINDINGS_FILE}")


if __name__ == "__main__":
    main()
