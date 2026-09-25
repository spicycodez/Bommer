# 💣 SMS Blast Bot

Telegram bot — SMS bombing with points system, admin panel, channel-backed DB.

## Deploy on Render (Free Plan)

1. Push this repo to GitHub
2. Render → New → Web Service → connect repo
3. Settings auto-load from `render.yaml`
4. Add env var: `PORT = 10000`

## File Structure

```
blast-bot/
├── main.py          ← bot (single file)
├── requirements.txt ← dependencies
├── render.yaml      ← render deploy config
├── Procfile         ← process config
└── .gitignore
```

## Storage

- Data auto-saves to Telegram channel `-1003942562029` (pinned message)
- Local `blast_data.json` as backup
- Admin Panel → Settings → Set Storage Channel se change kar sakte ho
