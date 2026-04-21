# 🦈 X Post Tracker — @IncomeSharks → Telegram

Automatically sends a Telegram message every time **@IncomeSharks** publishes a new original post on X (Twitter). Replies and retweets are silently skipped.

---

## How it works (plain English)

```
Every hour
  └─ GitHub Actions wakes up
       └─ Runs tracker.py
            ├─ Fetches RSS feed from RSSHub
            ├─ Skips posts already seen (stored in seen_ids.json)
            ├─ Skips replies (@…) and retweets (RT @…)
            ├─ Sends a Telegram message for every new original post
            └─ Commits updated seen_ids.json back to this repo
```

---

## One-time setup (do this once, ~10 minutes)

### Step 1 — Fork this repository

1. Open this repo on GitHub.
2. Click the **Fork** button (top-right).
3. You now have your own private copy.

---

### Step 2 — Create a Telegram Bot and get its token

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts.
3. Copy the token it gives you — it looks like `123456789:ABCdef…`

---

### Step 3 — Get your Telegram Chat ID

You need the ID of the chat where the bot will post.

**Easiest method:**
1. Add your new bot to a group, **or** just send it any message in a private chat.
2. Open this URL in your browser (replace `<TOKEN>` with your token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. Look for `"chat":{"id":` in the JSON response. That number is your Chat ID.
   - Private chat IDs are positive numbers (e.g. `987654321`).
   - Group chat IDs are negative numbers (e.g. `-1001234567890`).

---

### Step 4 — Add secrets to your GitHub repo

1. Go to your forked repo on GitHub.
2. Click **Settings → Secrets and variables → Actions → New repository secret**.
3. Add these two secrets:

| Secret name          | Value                          |
|----------------------|--------------------------------|
| `TELEGRAM_BOT_TOKEN` | the token from Step 2          |
| `TELEGRAM_CHAT_ID`   | the chat ID from Step 3        |

---

### Step 5 — Enable GitHub Actions

1. Click the **Actions** tab in your repo.
2. If prompted, click **"I understand my workflows, go ahead and enable them"**.
3. Done! The workflow will now run automatically every hour.

---

### Step 6 — Test it manually (optional but recommended)

1. Click **Actions** → **X Post Tracker** → **Run workflow** → **Run workflow**.
2. Watch the logs. If everything is green, check your Telegram for a message.

---

## Files in this repo

| File | Purpose |
|------|---------|
| `tracker.py` | The main Python script |
| `.github/workflows/tracker.yml` | The GitHub Actions schedule & steps |
| `seen_ids.json` | Tracks which posts were already sent (auto-updated) |
| `README.md` | This file |

---

## Telegram message format

```
🦈 New post from @IncomeSharks

{post text, up to 300 characters}

→ https://x.com/IncomeSharks/status/…
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No messages arriving | Check the Actions log for errors; verify your secrets are correct |
| Getting old posts on first run | Normal — the first run marks all current posts as seen without sending them… wait, actually it WILL send them. To silence the first run, pre-populate `seen_ids.json` by running the script locally first. |
| `bozo` RSS error | RSSHub may be temporarily down; the next hourly run will retry automatically |
| Bot can't send to group | Make sure you added the bot to the group and sent at least one message |

---

## Dependencies

- [`requests`](https://pypi.org/project/requests/) — HTTP calls to Telegram
- [`feedparser`](https://pypi.org/project/feedparser/) — RSS parsing

Both are installed automatically by the GitHub Actions workflow. No `requirements.txt` needed.
