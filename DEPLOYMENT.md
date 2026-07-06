# 🚀 Detailed Cloud Deployment Guide (24/7 Free Hosting)

This guide walks you through the exact, step-by-step process of hosting your Deals Bot for free on **Render.com** using **GitHub**. This ensures your bot runs 24/7 in the cloud without keeping your personal computer turned on.

---

## 🛠️ Step 1: Generate Your Cloud Session (On Your PC)

Before we upload anything to the internet, we need to log in to Telegram on your local PC and generate a special "session key". This key tells the cloud server that it's allowed to read your channels.

1. Open your terminal (Command Prompt or PowerShell) and navigate to the `Deals Telegram Bot` folder.
2. Run the setup script:
   ```bash
   python setup.py
   ```
3. The script will ask you for 4 pieces of information:
   - **API ID**: Get this from [my.telegram.org](https://my.telegram.org) (under API development tools).
   - **API Hash**: Get this from the same place.
   - **Bot Token**: Get this by messaging `@BotFather` on Telegram and typing `/newbot`.
   - **User ID**: Get this by messaging `@userinfobot` on Telegram and copying the numeric ID.
4. **Log in to Telegram**: The script will ask for your phone number (include your country code, e.g., `+91...`). Telegram will send a login code to your Telegram app. Type that code into the terminal.
5. The script will finish and output a massive block of text labeled **`TELEGRAM_STRING_SESSION`**. 
   > ⚠️ **Copy this string and paste it in a Notepad file immediately!** This is your master key. Never share it publicly.

---

## 🐙 Step 2: Push Your Code to GitHub

Render.com needs a place to download your code from. GitHub is the easiest way.

### Option A: Using the GitHub Website (Easiest for Beginners)
1. Go to [GitHub.com](https://github.com) and create a free account (if you don't have one).
2. Look for the **"+"** icon in the top right corner and click **"New repository"**.
3. Fill in the details:
   - **Repository name**: `deals-notification-bot` (or whatever you prefer)
   - **Visibility**: Select **Private** (Important: Keep it private so no one copies your code).
   - Uncheck "Add a README file".
   - Click **Create repository**.
4. You will see a screen titled "Quick setup". Look for the link that says **"uploading an existing file"** and click it.
5. Drag and drop ONLY the following files from your PC into the GitHub window:
   - `bot.py`
   - `requirements.txt`
   - `README.md`
   - `IMPLEMENTATION.md`
   - `DEPLOYMENT.md`
   > 🚨 **DO NOT UPLOAD `.env` or `setup.py`!** These contain your passwords. Keep them on your PC only.
6. Scroll down and click the green **"Commit changes"** button.

---

## ☁️ Step 3: Deploy on Render.com

Now we connect Render to your GitHub so it can run your Python code.

1. Go to [Render.com](https://render.com) and sign up using the **"GitHub"** button.
2. Once logged in, click the **"New"** button in the top right dashboard.
3. Select **"Background Worker"** from the dropdown menu.
   > *Why Background Worker?* Render has "Web Services" which go to sleep after 15 minutes of inactivity. Background Workers run continuously 24/7, making them perfect for Telegram bots.
4. On the next screen, look under "Connect a repository" and click your `deals-notification-bot` repository. (You may need to click "Configure account" to give Render permission to see your private GitHub repos).
5. You are now on the configuration page. Fill it out exactly like this:
   - **Name**: `DealsBot-Worker`
   - **Region**: (Leave as default)
   - **Branch**: `main` (or `master`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Select the **Free** tier (0.1 CPU, 512MB RAM).

---

## 🔐 Step 4: Add Your Secret Environment Variables

Scroll down the configuration page until you see the **Environment Variables** section. Click **"Add Environment Variable"**. 

You must add **5 variables** here. The names must be exact, and the values should be pasted from your Notepad file (the ones you got in Step 1).

| Key | Value (Example) |
|-----|-----------------|
| `TELEGRAM_API_ID` | `1234567` |
| `TELEGRAM_API_HASH` | `abcdef1234567890abcdef` |
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABCdefGhIJKlm...` |
| `TELEGRAM_USER_ID` | `123456789` |
| `TELEGRAM_STRING_SESSION` | `1Bjwxyz... (the massive string from Step 1)` |

*Ensure there are no extra spaces at the beginning or end of your values.*

---

## 🎉 Step 5: Start the Bot

1. Scroll to the very bottom and click **Create Background Worker**.
2. Render will take you to a dashboard with a black terminal window (Logs).
3. Wait 2-3 minutes while Render downloads Python, installs `telethon` (from your requirements.txt), and starts the bot.
4. Watch the logs. When you see this line:
   ```
   [INFO] User Client connected.
   Bot is online and ready!
   ```
   **You are officially deployed!** 🥳

---

## 📱 Step 6: Control Your Bot from Telegram

Now that the bot is running in the cloud 24/7, you can close your PC. 

Pick up your phone, open Telegram, and search for the bot you created with `@BotFather`.
1. Send `/start` or `/help` to wake up the menu.
2. Send `/channels` to see all your channels. Tap the inline buttons to turn monitoring ON for specific channels.
3. Send `/add_keyword deal` to add keywords.

*(Remember: Whenever you change a setting here, the bot saves it inside the chat history, so your settings are safe even if Render restarts the server tomorrow!)*
