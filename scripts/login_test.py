import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
DEBUG_DIR = ROOT / "debug"
DEBUG_DIR.mkdir(exist_ok=True)

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("INSTAGRAM_USERNAME o INSTAGRAM_PASSWORD mancanti nei GitHub Secrets.")


def screenshot(page, name):
    path = DEBUG_DIR / name
    page.screenshot(path=str(path), full_page=True)
    print(f"Screenshot salvato: {path}")


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox"]
    )

    context = browser.new_context(
        viewport={"width": 1365, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )

    page = context.new_page()

    print("Apro pagina login Instagram...")
    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(8000)
    screenshot(page, "01-login-page.png")

    try:
        print("Compilo username/password usando input index...")

        inputs = page.locator("input")
        input_count = inputs.count()
        print(f"Input trovati: {input_count}")

        if input_count < 2:
            screenshot(page, "98-no-inputs.png")
            raise RuntimeError("Non trovo almeno 2 campi input nella pagina login.")

        inputs.nth(0).fill(USERNAME)
        inputs.nth(1).fill(PASSWORD)

        screenshot(page, "02-filled-form.png")

        print("Invio login...")
        page.locator("button").filter(has_text="Log in").click(timeout=15000)

        page.wait_for_timeout(25000)
        screenshot(page, "03-after-submit.png")

        current_url = page.url
        print(f"URL dopo login: {current_url}")

        if "challenge" in current_url:
            print("RISULTATO: Instagram richiede challenge/verifica.")
        elif "accounts/login" in current_url:
            print("RISULTATO: siamo ancora sulla pagina login.")
        elif "instagram.com" in current_url:
            print("RISULTATO: possibile login riuscito.")
        else:
            print("RISULTATO: situazione non chiara.")

    except PlaywrightTimeoutError as e:
        print(f"TIMEOUT: {e}")
        screenshot(page, "99-timeout.png")
        raise

    except Exception as e:
        print(f"ERRORE: {e}")
        screenshot(page, "99-error.png")
        raise

    finally:
        browser.close()
