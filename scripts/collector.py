import json
import os
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS_FILE = ROOT / "data" / "accounts.txt"
FINDINGS_FILE = ROOT / "data" / "findings.json"

MAX_LINKS_PER_ACCOUNT = 6


def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return [line.strip().replace("@", "") for line in f if line.strip()]


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_number(raw):
    if not raw:
        return None

    raw = raw.strip().replace(",", "")

    multiplier = 1
    if raw.lower().endswith("k"):
        multiplier = 1000
        raw = raw[:-1]
    elif raw.lower().endswith("m"):
        multiplier = 1000000
        raw = raw[:-1]

    try:
        return int(float(raw) * multiplier)
    except Exception:
        return None


def extract_metrics(text):
    likes = None
    comments = None

    like_match = re.search(r"([\d,.]+[KkMm]?)\s+likes", text)
    comment_match = re.search(r"([\d,.]+[KkMm]?)\s+comments", text)

    if like_match:
        likes = parse_number(like_match.group(1))

    if comment_match:
        comments = parse_number(comment_match.group(1))

    return likes, comments


def make_score(likes, comments, content_type):
    score = 10 if content_type == "reel" else 5

    if likes:
        score += min(int(likes / 100), 500)

    if comments:
        score += min(int(comments * 2), 300)

    return score


def instagram_login(page):
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not username or not password:
        print("Instagram secrets non presenti.")
        return False

    print("Provo login Instagram...")

    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    try:
        page.fill("input[name='username']", username, timeout=15000)
        page.fill("input[name='password']", password, timeout=15000)
        page.click("button[type='submit']", timeout=15000)
        page.wait_for_timeout(15000)

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


def collect_account_links(page, account):
    profile_url = f"https://www.instagram.com/{account}/"

    print(f"Analizzo account: @{account}")

    try:
        page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(9000)

        # chiude eventuali popup non critici
        for text in ["Not Now", "Non ora", "Close", "Chiudi"]:
            try:
                page.get_by_text(text).click(timeout=1500)
                page.wait_for_timeout(1000)
            except Exception:
                pass

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

        return links[:MAX_LINKS_PER_ACCOUNT]

    except Exception as e:
        print(f"Errore account @{account}: {e}")
        return []


def extract_content_metadata(page, url, fallback_account):
    metadata = {
        "caption": "",
        "title": "",
        "likes": None,
        "comments": None
    }

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)

        page_title = ""
        try:
            page_title = page.title()
        except Exception:
            pass

        meta_description = ""
        try:
            meta_description = page.locator("meta[property='og:description']").get_attribute("content", timeout=5000)
        except Exception:
            pass

        og_title = ""
        try:
            og_title = page.locator("meta[property='og:title']").get_attribute("content", timeout=5000)
        except Exception:
            pass

        text_content = ""
        try:
            text_content = page.locator("article").inner_text(timeout=8000)
        except Exception:
            pass

        combined = clean_text(" ".join([
            page_title or "",
            og_title or "",
            meta_description or "",
            text_content or ""
        ]))

        likes, comments = extract_metrics(combined)

        metadata["caption"] = combined[:700]
        metadata["title"] = clean_text(page_title or og_title or f"Instagram content by {fallback_account}")
        metadata["likes"] = likes
        metadata["comments"] = comments

        return metadata

    except Exception as e:
        print(f"Errore metadata su {url}: {e}")
        return metadata


def make_item(account, url, metadata):
    today = datetime.now().strftime("%Y-%m-%d")
    content_type = "reel" if "/reel/" in url else "post"

    likes = metadata.get("likes")
    comments = metadata.get("comments")

    return {
        "date_found": today,
        "platform": "Instagram",
        "source_keyword": f"@{account}",
        "content_url": url,
        "account": account,
        "title": metadata.get("title", f"Instagram {content_type} by {account}"),
        "views": None,
        "likes": likes,
        "comments": comments,
        "traffic_score": make_score(likes, comments, content_type),
        "content_type": content_type,
        "observed_theme": metadata.get("caption", ""),
        "hook": "",
        "visual_pattern": "",
        "audio_or_text_pattern": "",
        "why_it_gets_attention": "",
        "copy_model": "",
        "adaptation_potential_for_irea": "",
        "screenshot_url": ""
    }


def main():
    accounts = load_accounts()
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

        for account in accounts:
            links = collect_account_links(page, account)

            for url in links:
                if url not in seen_urls:
                    seen_urls.add(url)
                    metadata = extract_content_metadata(page, url, account)
                    findings.append(make_item(account, url, metadata))

        browser.close()

    findings = sorted(findings, key=lambda x: x.get("traffic_score", 0), reverse=True)

    with open(FINDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    print(f"Salvati {len(findings)} contenuti Instagram in {FINDINGS_FILE}")


if __name__ == "__main__":
    main()
