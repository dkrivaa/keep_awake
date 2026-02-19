import os
import json
import time
from playwright.sync_api import sync_playwright


def wake_app(url: str, index: int, retries: int = 3) -> bool:
    for attempt in range(1, retries + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, timeout=60000)
                time.sleep(10)
                page.screenshot(path=f"screenshot_{index}_before.png")

                try:
                    wake_button = page.get_by_text("Yes, get this app back up!")
                    if wake_button.is_visible(timeout=5000):
                        print(f"  Sleep screen detected for {url}, clicking...")
                        wake_button.click()
                        print(f"  Clicked wake button for {url}")
                        time.sleep(30)  # wait for app to boot
                        page.screenshot(path=f"screenshot_{index}_after.png")
                    else:
                        print(f"  App already awake: {url}")
                except Exception as e:
                    print(f"  Button check failed: {e}")

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

    results = {url: wake_app(url, index) for index, url in enumerate(urls)}
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

