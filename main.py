import os
import requests
import time
import json
from datetime import datetime


def wake_app(url: str, timeout: int = 60, retries: int = 3) -> bool:
    """
    Ping a Streamlit app URL. Retries on failure since sleeping apps
    take time to spin up and may return errors on the first request.
    """
    print(f"\n[{datetime.utcnow().isoformat()}] Waking: {url}")

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            print(f"  Attempt {attempt}: HTTP {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ App is awake!")
                return True
        except requests.exceptions.Timeout:
            print(f"  Attempt {attempt}: Timed out (app may still be waking)")
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt}: Error — {e}")

        if attempt < retries:
            wait = attempt * 15  # 15s, 30s between retries
            print(f"  Waiting {wait}s before retry...")
            time.sleep(wait)

    print(f"  ✗ Failed to wake after {retries} attempts.")
    return False


def main():
    # Load URLs from environment variable (JSON array string)
    # e.g. APP_URLS = '["https://myapp.streamlit.app", "https://otherapp.streamlit.app"]'
    raw = os.environ.get("APP_URLS", "")
    if not raw:
        print("No APP_URLS environment variable set. Exiting.")
        return

    try:
        urls = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: treat as newline or comma-separated
        urls = [u.strip() for u in raw.replace(",", "\n").splitlines() if u.strip()]

    print(f"Keeping {len(urls)} app(s) alive...")
    results = {url: wake_app(url) for url in urls}

    print("\n--- Summary ---")
    for url, success in results.items():
        status = "✓ Awake" if success else "✗ Failed"
        print(f"  {status}: {url}")

    if not all(results.values()):
        raise SystemExit(1)  # Fail the workflow if any app didn't respond


if __name__ == "__main__":
    main()
