import os
import json
import feedparser
import requests

# ── Settings ────────────────────────────────────────────────────────────────
RSS_URL        = "https://rsshub.app/twitter/user/IncomeSharks"
SEEN_IDS_FILE  = "seen_ids.json"
BOT_TOKEN      = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID        = os.environ["TELEGRAM_CHAT_ID"]
MAX_TEXT_LEN   = 300


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_seen_ids():
    """Read the list of already-sent post IDs from the JSON file."""
    with open(SEEN_IDS_FILE, "r") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids):
    """Write the updated set of post IDs back to the JSON file."""
    with open(SEEN_IDS_FILE, "w") as f:
        json.dump(list(seen_ids), f, indent=2)


def is_reply(entry):
    """
    Return True if this post is a reply or retweet.
    Replies start with '@'.  Retweets start with 'RT @'.
    We check both the title and the summary (description).
    """
    title   = (entry.get("title")   or "").strip()
    summary = (entry.get("summary") or "").strip()
    for text in (title, summary):
        if text.startswith("@") or text.startswith("RT @"):
            return True
    return False


def send_telegram(text, link):
    """Send one Telegram message."""
    body = (
        f"🦈 New post from @IncomeSharks\n\n"
        f"{text}\n\n"
        f"→ {link}"
    )
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": CHAT_ID, "text": body})
    resp.raise_for_status()          # crash loudly if Telegram says no
    print(f"  ✅ Sent: {link}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("Fetching RSS feed …")
    feed = feedparser.parse(RSS_URL)

    if feed.bozo:                    # feedparser sets this on parse errors
        raise RuntimeError(f"RSS parse error: {feed.bozo_exception}")

    entries = feed.entries
    print(f"Found {len(entries)} items in feed.")

    seen_ids = load_seen_ids()
    new_count = 0

    for entry in entries:
        post_id = entry.get("id") or entry.get("link")
        if not post_id:
            continue

        if post_id in seen_ids:
            continue                 # already processed

        if is_reply(entry):
            print(f"  ⏭  Skipping reply/RT: {post_id}")
            seen_ids.add(post_id)   # still mark as seen so we don't check again
            continue

        # Build the text preview
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
