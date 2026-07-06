# 🚀 Free Cloud Deployment Guide (24/7 Hosting)

You noticed that Render removed their free tier for "Background Workers." You are correct! Because platforms like Vercel and Netlify are "Serverless" (they immediately kill your code after loading a webpage), they **cannot** run Telegram bots that need a constant 24/7 connection.

To bypass Render's limits and host this bot 100% for free, we use the **"Dummy Web Server Workaround"**. 
I have updated your `bot.py` to include a tiny fake web server. Render will think you are hosting a website (which they allow for free), and we will use a free pinging service to prevent Render from putting it to sleep!

---

## 🛠️ Step 1: Generate Your Cloud Session (On Your PC)

1. Open your terminal and run `python setup.py`
2. Follow the prompts to log in.
3. Copy the huge **`TELEGRAM_STRING_SESSION`** it prints out. Keep it safe!

---

## 🐙 Step 2: Push Your Code to GitHub

1. Go to [GitHub.com](https://github.com) and create a **New Private Repository** (e.g., `deals-bot`).
2. Upload these files to GitHub:
   - `bot.py`
   - `requirements.txt`
   - `README.md`
   - `DEPLOYMENT.md`
   *(Do NOT upload your `.env` or `setup.py`!)*

---

## ☁️ Step 3: Deploy on Render.com (As a Web Service)

1. Go to [Render.com](https://render.com) and sign in with GitHub.
2. Click **New** and select **"Web Service"** (NOT Background Worker).
3. Connect your `deals-bot` repository.
4. Fill out the configuration exactly like this:
   - **Name**: `DealsBot`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: **Free**

5. Scroll down to **Environment Variables** and add your 5 secrets:
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_USER_ID`
   - `TELEGRAM_STRING_SESSION`

6. Click **Create Web Service**. 
7. Wait 3-4 minutes. At the top left of the Render dashboard, you will see a URL generated for you (e.g., `https://dealsbot-abc1.onrender.com`). **Copy this URL.**

---

## ⏰ Step 4: The Keep-Alive Trick (Crucial!)

Render's free Web Services go to sleep if no one visits their URL for 15 minutes. To keep your bot awake 24/7:

1. Go to [cron-job.org](https://cron-job.org) (or UptimeRobot.com) and create a free account.
2. Click **Create Cronjob**.
3. **URL**: Paste the Render URL you copied in Step 3.
4. **Execution schedule**: Set it to run **every 14 minutes**.
5. Click **Create**.

**Done!** The cron job will now "visit" your bot's fake web server every 14 minutes. Render will think you have active website traffic, and it will never put your bot to sleep. Your Telegram Bot will run 24/7 entirely for free!

---

## 🌟 Alternative Platform: Koyeb

If you don't want to use the Render workaround, the best alternative right now is **[Koyeb.com](https://koyeb.com)**.
Koyeb offers an "Eco Free Tier" that natively supports Docker containers and Background Workers running 24/7 without needing the ping trick! 
To deploy there: Just connect GitHub, select your repo, set the Run Command to `python bot.py`, and add the exact same 5 Environment Variables.
