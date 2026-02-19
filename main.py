import os
import json
import time
from playwright.sync_api import sync_playwright


def wake_app(url: str, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, timeout=60000)
                time.sleep(30)  # wait for app to fully load
                browser.close()
            print(f"✓ {url}")
            return True
        except Exception as e:
            print(f"✗ Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                time.sleep(attempt * 15)
    print(f"✗ {url} failed after {retries} attempts")
    return False


def main():
    raw = os.environ.get("APP_URLS", "")
    if not raw:
        return
    try:
        urls = json.loads(raw)
    except json.JSONDecodeError:
        urls = [u.strip() for u in raw.replace(",", "\n").splitlines() if u.strip()]

    results = {url: wake_app(url) for url in urls}
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()