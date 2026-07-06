# Deals Notification Bot (Cloud & Chat-Controlled)

A **free** Python bot that monitors your selected Telegram **channels** for deal keywords and sends you a **real push notification via your Telegram bot** — so your phone buzzes instantly.

This version is designed to be **100% controllable from Telegram** (no need to edit config files) and is perfect for deploying on free cloud hosts (like Render or Koyeb) because it saves its configuration natively inside Telegram!

---

## How It Works

```
Your Telegram Account (Telethon)
         │
         ├── Monitors selected channels silently
         │
         └── Keyword Match Found?
                    │
                    └──► Your Telegram Bot sends you a message
                                    │
                                    └──► 📱 Push notification on your phone!
```

---

## Bot Commands (Control via Telegram)

Once running, you can talk to your bot directly to manage everything:

| Command | What it does |
|---------|--------------|
| `/help` | Shows available commands |
| `/channels` | Gives you an interactive menu with **inline buttons** to tap and toggle your channels ON/OFF |
| `/status` | Shows how many channels and keywords are active |
| `/keywords` | Lists your current keywords |
| `/add_keyword <word1, word2>` | Adds new keywords to watch (supports comma-separated lists) |
| `/remove_keyword <word1, word2>` | Removes keywords (supports comma-separated lists) |
| `/clear_channels` | Instantly stops watching all channels |
| `/clear_keywords` | Removes all keywords |
| `/clear_chat` | 🗑️ Manually deletes all old deal notifications (keeps your settings safe) |
| `/toggle_cleanup` | ⚙️ Turns the 24/7 background Auto-Cleaner ON or OFF |

---

## ☁️ How does it save my settings?

Free cloud servers (like Render) delete all files when they restart. To solve this, this bot uses **Telegram-Native Storage**. 

When you configure channels or keywords, the bot sends a hidden `#CONFIG_DATA` message to your chat and pins it. When the server restarts, the bot simply reads its own message to remember your settings! 

*You never have to worry about losing your settings, and you don't need a database.*

---

## Local Setup (Running on your PC)

If you just want to run it on your own computer:

1. Install Python 3.11+
2. Run `pip install -r requirements.txt`
3. Run `python setup.py` and follow the prompts to get your credentials.
4. Double-click `run_bot.bat` or run `python bot.py`.

---

## Cloud Deployment (Run 24/7 for Free)

See the detailed **Deployment Guide** artifact for step-by-step instructions on hosting this on GitHub and Render.com!

---

## Notification Format

When a deal is found, your bot sends you:

```
🔔 Deal Alert!

📢 Channel: TechDeals India
🔑 Keyword: deal, off

💬 Message:
"HUGE deal! 60% off on realme buds, grab now before it ends..."

👉 View Original Message

⏰ 04:23 PM  •  #deal #off
```
