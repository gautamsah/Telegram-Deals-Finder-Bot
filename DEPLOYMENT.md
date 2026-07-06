# 🚀 Detailed Cloud Deployment Guide (24/7 Hosting)

Because platforms like Vercel and Netlify are "Serverless" (they immediately kill your code after loading a webpage), they **cannot** run Telegram bots that need a constant 24/7 connection.

To bypass Render's limits and host this bot 100% for free, we use the **"Dummy Web Server Workaround"**. 
The `bot.py` file includes a tiny fake web server. Render will think you are hosting a website (which they allow for free), and we will use a free pinging service to prevent Render from putting it to sleep!

---

## 🛠️ Step 1: Generate Your Cloud Session (On Your PC)

Before we upload anything to the internet, we need to log in to Telegram on your local PC and generate a special "session key".

1. Open your terminal in the folder where your bot files are.
2. Run the command: `python setup.py`
3. The script will ask you for your API ID, API Hash, Bot Token, and User ID. 
4. **Log in to Telegram**: Enter your phone number (e.g., `+91...`). Telegram will send a code to your phone. Type it into the terminal.
5. The script will finish and print out a massive block of text labeled **`TELEGRAM_STRING_SESSION`**. 
   > ⚠️ **Copy this string and keep it safe!** This is your master key. Never share it publicly.

---

## 🐙 Step 2: Push Your Code to GitHub

Render.com needs a place to download your code from. GitHub is the easiest way.

1. Go to [GitHub.com](https://github.com) and create a free account (if you don't have one).
2. Look for the **"+"** icon in the top right corner and click **"New repository"**.
3. Fill in the details:
   - **Repository name**: `deals-bot`
   - **Visibility**: Public or Private (Private is recommended, but Public is fine as long as you do not upload your secrets).
   - Click **Create repository**.
4. Click on the link that says **"uploading an existing file"**.
5. Drag and drop these files from your PC into GitHub:
   - `bot.py`
   - `requirements.txt`
   - `README.md`
   - `DEPLOYMENT.md`
   - `IMPLEMENTATION.md`
   > 🚨 **DO NOT UPLOAD `.env`!** Your `.env` file contains your passwords. It is perfectly safe to upload `setup.py` (since it contains no passwords), but `.env` must stay on your PC only!
6. Click the green **"Commit changes"** button.

---

## ☁️ Step 3: Deploy on Render.com (As a Web Service)

1. Go to [Render.com](https://render.com) and sign up using the **"GitHub"** button.
2. Click the **"New"** button in the top right and select **"Web Service"** (NOT Background Worker).
3. Connect your GitHub account and select your `deals-bot` repository.
4. Fill out the configuration exactly like this:
   - **Name**: `DealsBot-Web`
   - **Branch**: `main` (or `master`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Select the **Free** tier (0.1 CPU, 512MB RAM).

5. Scroll down to **Environment Variables**. Click "Add Environment Variable" 5 times, and add these exact keys along with the values you generated in Step 1:
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_USER_ID`
   - `TELEGRAM_STRING_SESSION`

6. Scroll to the bottom and click **Create Web Service**. 
7. Render will now build your bot. Wait 3-4 minutes. Look at the top left of the dashboard — Render will generate a web address for you (e.g., `https://dealsbot-web.onrender.com`). **Copy this URL.**

---

## ⏰ Step 4: The Keep-Alive Trick (Crucial!)

Render's free Web Services will automatically shut down if no one visits their URL for 15 minutes. To keep your bot awake 24/7, we will set up a robot to "visit" the site for you.

1. Go to [cron-job.org](https://cron-job.org) (or UptimeRobot.com) and create a free account.
2. Once logged in, click **Create Cronjob** or **Add New Monitor**.
3. **URL**: Paste the Render URL you copied in Step 3 (e.g., `https://dealsbot-web.onrender.com`).
4. **Schedule**: Set it to run **every 14 minutes**.
5. Click **Create** or **Save**.

**You are completely done!** The cron job will now ping your fake web server every 14 minutes. Render will think you have active website traffic, and your Telegram Bot will run 24/7 entirely for free!

You can now open Telegram, message your Bot, and send `/help` to start adding channels and keywords!

---

## 🌟 Alternative Platform: Koyeb

If you find Render too complicated, the best alternative right now is **[Koyeb.com](https://koyeb.com)**.
Koyeb offers an "Eco Free Tier" that natively supports Background Workers running 24/7 — meaning you don't need to do Step 4 (the keep-alive ping trick)! 

To deploy on Koyeb: 
1. Sign up, connect GitHub, and select your repo.
2. Set the Run Command to `python bot.py`.
3. Add the exact same 5 Environment Variables.
4. Click Deploy.
