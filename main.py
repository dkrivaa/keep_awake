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

                # Check if the app is sleeping and click the wake button
                try:
                    wake_button = page.get_by_test_id("wakeup-button-owner")
                    if wake_button.is_visible(timeout=5000):
                        wake_button.click()
                        print(f"  Clicked wake button for {url}")
                except Exception:
                    pass  # No sleep screen, app was already awake

                # Wait for the app to fully load
                page.wait_for_load_state("networkidle", timeout=120000)
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

