"""
setup.py - Cloud Deployment Setup Wizard
Run this ONCE to get your credentials for hosting (like Render).
"""

import os
import sys
import asyncio

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from colorama import Fore, Style, init as colorama_init
    from dotenv import set_key, dotenv_values
except ImportError:
    print("\n[!] Missing dependencies. Run:\n    pip install -r requirements.txt\n")
    sys.exit(1)

colorama_init(autoreset=True)
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")

def prompt(label: str, default: str = "", secret: bool = False) -> str:
    display = f"[hidden]" if (secret and default) else (f"[{default}]" if default else "")
    suffix = f" {display}" if display else ""
    try:
        val = input(f"  → {label}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        return default
    return val if val else default

def load_env() -> dict:
    if os.path.exists(ENV_FILE): return dotenv_values(ENV_FILE)
    return {}

def save_env_key(key: str, value: str):
    # Read existing
    lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    # Update or add
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
            
    if not found:
        lines.append(f"{key}={value}\n")
        
    # Write back
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
async def main():
    print(Fore.CYAN + "=== Deals Bot Cloud Setup ===" + Style.RESET_ALL)
    existing = load_env()

    print("\n1. Telegram API Credentials (from my.telegram.org)")
    api_id = prompt("API ID", existing.get("TELEGRAM_API_ID", ""))
    api_hash = prompt("API Hash", existing.get("TELEGRAM_API_HASH", ""))

    print("\n2. Bot Credentials")
    bot_token = prompt("Bot Token (from @BotFather)", existing.get("TELEGRAM_BOT_TOKEN", ""))
    user_id = prompt("Your Telegram User ID (from @userinfobot)", existing.get("TELEGRAM_USER_ID", ""))

    if not all([api_id, api_hash, bot_token, user_id]):
        print(Fore.RED + "All fields are required!" + Style.RESET_ALL)
        sys.exit(1)

    save_env_key("TELEGRAM_API_ID", api_id)
    save_env_key("TELEGRAM_API_HASH", api_hash)
    save_env_key("TELEGRAM_BOT_TOKEN", bot_token)
    save_env_key("TELEGRAM_USER_ID", user_id)

    print("\n3. Generating Cloud Session...")
    print("You will need to log into your Telegram account now.")
    
    # Use StringSession so it can be copied to cloud hosting easily
    client = TelegramClient(StringSession(), int(api_id), api_hash)
    await client.start()
    
    session_str = client.session.save()
    save_env_key("TELEGRAM_STRING_SESSION", session_str)
    
    await client.disconnect()

    print(Fore.GREEN + "\n✅ Setup Complete!" + Style.RESET_ALL)
    print("All credentials have been saved to .env")
    print("\nIf you are deploying to Render or Koyeb, add these environment variables:")
    print(f"TELEGRAM_API_ID = {api_id}")
    print(f"TELEGRAM_API_HASH = {api_hash}")
    print(f"TELEGRAM_BOT_TOKEN = {bot_token}")
    print(f"TELEGRAM_USER_ID = {user_id}")
    print(f"TELEGRAM_STRING_SESSION = {session_str}")
    print("\nTo start locally, just run: python bot.py")

if __name__ == "__main__":
    asyncio.run(main())
