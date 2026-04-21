import os
import json
import feedparser
import requests

# ── Settings ────────────────────────────────────────────────────────────────
RSS_URL        = "https://rsshub.rss.plus/twitter/user/IncomeSharks"
SEEN_IDS_FILE  = "seen_ids.json"
BOT_TOKEN      = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID        = os.environ["TELEGRAM_CHAT_ID"]
MAX_TEXT_LEN   = 300

# Pretend to be a real browser so RSSHub doesn't block us
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_seen_ids():
    with open(SEEN_IDS_FILE, "r") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids):
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(seen_ids), f, indent=2)


def is_reply(entry):
    title   = (entry.get("title")   or "").strip()
    summary = (entry.get("summary") or "").strip()
    for text in (title, summary):
        if text.startswith("@") or text.startswith("RT @"):
            return True
    return False


def send_telegram(text, link):
    body = (
        f"🦈 New post from @IncomeSharks\n\n"
        f"{text}\n\n"
        f"→ {link}"
    )
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": CHAT_ID, "text": body})
    resp.raise_for_status()
    print(f"  ✅ Sent: {link}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("Fetching RSS feed …")

    # Fetch raw XML ourselves with browser-like headers
    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Could not reach RSSHub: {e}")
        print("Skipping this run — will retry next hour.")
        return

    # Parse the XML
    feed = feedparser.parse(resp.text)

    # If still broken, exit cleanly instead of crashing
    if feed.bozo and not feed.entries:
        print(f"⚠️  RSS feed returned invalid XML: {feed.bozo_exception}")
        print("Skipping this run — will retry next hour.")
        return

    entries = feed.entries
    print(f"Found {len(entries)} items in feed.")

    seen_ids = load_seen_ids()
    new_count = 0

    for entry in entries:
        post_id = entry.get("id") or entry.get("link")
        if not post_id:
            continue

        if post_id in seen_ids:
            continue

        if is_reply(entry):
            print(f"  ⏭  Skipping reply/RT: {post_id}")
            seen_ids.add(post_id)
            continue

        raw_text = (entry.get("title") or entry.get("summary") or "").strip()
        preview  = raw_text[:MAX_TEXT_LEN] + ("…" if len(raw_text) > MAX_TEXT_LEN else "")
        link     = entry.get("link", "")

        send_telegram(preview, link)
        seen_ids.add(post_id)
        new_count += 1

    save_seen_ids(seen_ids)
    print(f"Done. {new_count} new post(s) sent.")


if __name__ == "__main__":
    main()
