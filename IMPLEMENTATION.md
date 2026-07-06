# 🛠️ Implementation Guide & Architecture

This document explains how the **Deals Notification Bot** works under the hood. If you want to modify the code or understand how it bypasses the limits of free cloud hosting, read on!

## Architecture Overview

The bot uses a **Dual-Client Architecture** powered by the `Telethon` Python library.

1. **The User Client**: Connects to Telegram as *you* (using your phone number/session). This is necessary because Telegram Bots cannot read messages in channels unless they are an Admin. Your user account reads the channels silently in the background.
2. **The Bot Client**: Connects to Telegram as your *Bot* (using the Bot Token). This client listens to your chat window, provides the slash commands (`/channels`, `/keywords`), and sends the push notifications to your phone when a deal is found.

Both clients run in the exact same `asyncio` event loop simultaneously inside `bot.py`.

---

## ☁️ The "Ephemeral Storage" Problem (And Solution)

### The Problem
Free cloud providers (like Render, Heroku, Koyeb) use **Ephemeral File Systems**. This means every time they restart your app (usually once every 24 hours), they wipe the hard drive clean and re-download your code from GitHub. 

If we used a standard `config.json` file to save your keywords and channels, all your settings would be deleted every single day.

### The Solution: Telegram-Native Storage
Instead of saving settings to a file or requiring you to set up a database (like MongoDB), the bot uses Telegram itself as the database.

**How it works:**
1. When the bot starts, it searches its own chat history with you for a message containing `#CONFIG_DATA`.
2. If it finds it, it extracts the JSON text from that message and loads your channels/keywords into memory.
3. If it doesn't find one (e.g., on first startup), it creates a new message with default settings and pins it to the chat.
4. Whenever you use a command like `/add_keyword` or tap an inline button to toggle a channel, the bot modifies the JSON in its memory and **edits the pinned message** to save the changes.

Because the data is stored in the Telegram cloud (inside the message text), it completely survives server restarts!

---

## Code Breakdown (`bot.py`)

### 1. `load_or_create_config()`
This function runs at startup. It uses `bot_client.iter_messages()` to search your chat history for the config message. 

### 2. `save_config()`
This function takes the `ACTIVE_CONFIG` Python dictionary, converts it to JSON, and edits the pinned `#CONFIG_DATA` message. It's called every time you make a change via a slash command.

### 3. `is_monitored_chat()`
This is the filter function for the User Client. When a message arrives in *any* channel you are a part of, this function checks if that channel's ID exists in your `ACTIVE_CONFIG` and is set to `"enabled": true`. If not, the message is ignored.

### 4. Cooldown System
To prevent spam (e.g., if a channel posts 5 messages about the same sale in 10 seconds), the bot tracks `COOLDOWNS`. When a deal is found in a channel, it records the timestamp. It will ignore any further deals from that specific channel for the next 15 seconds (configurable).

### 5. Inline Keyboard Pagination
The `/channels` command generates Inline Buttons. Since you might be subscribed to 50+ channels, the bot automatically paginates them (10 per page) using the `build_channel_buttons()` function and the `CallbackQuery` event handler.

---

## Extending the Bot

If you want to add more features, here is where to look:

- **Adding a new slash command**: Look at the `@bot_client.on(events.NewMessage(pattern=...))` decorators. Just copy one of the existing commands (like `/status`) and modify the regex pattern.
- **Advanced Filtering**: Look at `find_matches()`. Currently, it uses simple Regex to find keywords. You could modify this to look for specific prices (e.g., regex for `₹[0-9]{1,3}`) or negative keywords (e.g., skip if it contains "out of stock").
