"""
bot.py — Deals Notification Bot (Cloud & Chat-Controlled Version)
──────────────────────────────────────────────────────────────────
Runs TWO Telegram clients simultaneously:
  1. Bot Client: Listens to your commands (/channels, /keywords) in chat.
  2. User Client: Listens to your joined channels for deals silently.

Config is stored natively IN THE BOT CHAT as a pinned message (#CONFIG_DATA),
meaning it survives server restarts on free ephemeral hosts (like Render).
"""

import os
import sys
import json
import asyncio
import logging
import re
import time
from datetime import datetime

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    from telethon import TelegramClient, events, Button
    from telethon.tl.types import PeerChannel, Channel
    from telethon.sessions import StringSession
    from dotenv import load_dotenv
    from colorama import Fore, Style, init as colorama_init
except ImportError:
    print("\n[!] Missing dependencies. Run:\n    pip install -r requirements.txt\n")
    sys.exit(1)

# ── Init ──────────────────────────────────────────────────────────────────────
colorama_init(autoreset=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ── Global State ──────────────────────────────────────────────────────────────
ACTIVE_CONFIG = {
    "channels": [],
    "keywords": ["deal", "off", "discount", "free", "sale"],
    "settings": {
        "cooldown_seconds": 15,
        "min_keyword_matches": 1
    }
}
CONFIG_MSG_ID = None

# Track cooldowns per channel {channel_id: timestamp}
COOLDOWNS: dict[int, float] = {}

# Compiled regex patterns
KEYWORD_PATTERNS = []

# All channels the user is part of (cached for the /channels command)
USER_CHANNELS = []

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_env(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        logger.error(f"Missing environment variable: {key}")
        sys.exit(1)
    return val

def compile_keywords():
    global KEYWORD_PATTERNS
    KEYWORD_PATTERNS = []
    for kw in ACTIVE_CONFIG["keywords"]:
        KEYWORD_PATTERNS.append(re.compile(re.escape(kw), re.IGNORECASE))

def find_matches(text: str) -> list[str]:
    matched = []
    for p in KEYWORD_PATTERNS:
        m = p.search(text)
        if m:
            matched.append(m.group(0))
    return matched

# ── Config Management (Telegram Native Storage) ───────────────────────────────

async def load_or_create_config(bot_client: TelegramClient, user_id: int):
    """Search the bot chat history for the #CONFIG_DATA message, or create it."""
    global ACTIVE_CONFIG, CONFIG_MSG_ID
    
    logger.info("Looking for existing config in bot chat...")
    
    # Search for our config message
    async for msg in bot_client.iter_messages(user_id, search="#CONFIG_DATA"):
        if msg.out: # Make sure it's from the bot
            try:
                # Extract JSON between markers
                json_str = msg.text.split("```json")[1].split("```")[0].strip()
                ACTIVE_CONFIG = json.loads(json_str)
                CONFIG_MSG_ID = msg.id
                logger.info("Loaded config from Telegram chat history!")
                compile_keywords()
                return
            except Exception as e:
                logger.warning(f"Found config message but couldn't parse it: {e}")
    
    # If not found, create a new one
    logger.info("No config found in chat. Creating a new pinned config message...")
    await save_config(bot_client, user_id)
    compile_keywords()

async def save_config(bot_client: TelegramClient, user_id: int):
    """Save the ACTIVE_CONFIG back to the Telegram chat as an edited message."""
    global CONFIG_MSG_ID
    
    json_str = json.dumps(ACTIVE_CONFIG, indent=2, ensure_ascii=False)
    text = (
        "⚙️ **Bot Configuration Data** ⚙️\n"
        "_(Do not delete this message! The bot uses it to remember your settings after restarts.)_\n\n"
        "#CONFIG_DATA\n"
        "```json\n"
        f"{json_str}\n"
        "```"
    )
    
    if CONFIG_MSG_ID:
        try:
            await bot_client.edit_message(user_id, CONFIG_MSG_ID, text)
        except Exception as e:
            logger.error(f"Failed to edit config msg, sending new one: {e}")
            CONFIG_MSG_ID = None
            
    if not CONFIG_MSG_ID:
        msg = await bot_client.send_message(user_id, text)
        CONFIG_MSG_ID = msg.id
        try:
            await bot_client.pin_message(user_id, msg.id, notify=False)
        except Exception:
            pass # Ignore if pin fails
            
    compile_keywords()

# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print(Fore.CYAN + "Starting Dual-Client Architecture..." + Style.RESET_ALL)

    api_id     = int(get_env("TELEGRAM_API_ID"))
    api_hash   = get_env("TELEGRAM_API_HASH")
    bot_token  = get_env("TELEGRAM_BOT_TOKEN")
    user_id    = int(get_env("TELEGRAM_USER_ID"))
    
    # Check for String Session (cloud) or local file
    string_session = os.environ.get("TELEGRAM_STRING_SESSION", "").strip()
    user_session = StringSession(string_session) if string_session else os.path.join(os.path.dirname(__file__), "user_session")

    # 1. Start Bot Client
    bot_client = TelegramClient("bot_session", api_id, api_hash)
    await bot_client.start(bot_token=bot_token)
    logger.info("Bot Client connected.")

    # Load Config from Chat
    await load_or_create_config(bot_client, user_id)

    # 2. Start User Client
    user_client = TelegramClient(user_session, api_id, api_hash)
    await user_client.start()
    logger.info("User Client connected.")
    
    # Cache user channels
    global USER_CHANNELS
    USER_CHANNELS = [d for d in await user_client.get_dialogs() if d.is_channel and not d.is_group]
    logger.info(f"Found {len(USER_CHANNELS)} channels in your account.")

    # ── User Client: Deal Listener ────────────────────────────────────────────
    
    def is_monitored_chat(chat_id: int) -> bool:
        """Filter function to only listen to enabled channels."""
        # Telethon chat IDs sometimes lack the -100 prefix, so we check both
        str_id = str(chat_id)
        alt_id = int(f"-100{str_id}") if not str_id.startswith("-100") else int(str_id[4:])
        
        for ch in ACTIVE_CONFIG["channels"]:
            if ch.get("enabled", True) and (ch["id"] == chat_id or ch["id"] == alt_id):
                return True
        return False

    @user_client.on(events.NewMessage(incoming=True))
    async def on_channel_message(event):
        if not is_monitored_chat(event.chat_id):
            return
            
        text = event.raw_text
        if not text or len(text.strip()) < 5:
            return

        matched = find_matches(text)
        if len(matched) < ACTIVE_CONFIG["settings"]["min_keyword_matches"]:
            return

        # Cooldown check
        ch_id = event.chat_id
        now = time.monotonic()
        cooldown = ACTIVE_CONFIG["settings"]["cooldown_seconds"]
        if now - COOLDOWNS.get(ch_id, 0) < cooldown:
            return
        COOLDOWNS[ch_id] = now

        # Get channel name
        ch_name = event.chat.title if event.chat else "Unknown Channel"
        
        # Format Alert
        kw_badge = "  ".join(f"#{k.replace(' ', '_')}" for k in matched[:5])
        preview = text[:400] + ("…" if len(text) > 400 else "")
        
        link = ""
        if hasattr(event.chat, "username") and event.chat.username:
            link = f"\n\n👉 [View Original Message](https://t.me/{event.chat.username}/{event.id})"
        else:
            peer_id = str(ch_id).replace("-100", "")
            link = f"\n\n👉 [View Original Message](https://t.me/c/{peer_id}/{event.id})"

        msg = (
            f"🔔 **Deal Alert!**\n\n"
            f"📢 **Channel:** {ch_name}\n"
            f"🔑 **Keyword:** {', '.join(matched)}\n\n"
            f"💬 **Message:**\n_{preview}_{link}\n\n"
            f"⏰ {datetime.now().strftime('%I:%M %p')}  •  {kw_badge}"
        )

        try:
            await bot_client.send_message(user_id, msg, link_preview=False)
            logger.info(f"Sent deal alert for {ch_name}")
        except Exception as e:
            logger.error(f"Failed to send deal alert: {e}")

    # ── Bot Client: Command Handlers ──────────────────────────────────────────
    
    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/start$|^/help$"))
    async def cmd_help(event):
        text = (
            "🤖 **Deals Notification Bot**\n\n"
            "I am monitoring your channels for deals. Use these commands to control me:\n\n"
            "📡 **/channels** — Select which channels to monitor\n"
            "🔑 **/keywords** — View and manage your keywords\n"
            "➕ **/add_keyword <word>** — Add a new keyword\n"
            "➖ **/remove_keyword <word>** — Remove a keyword\n"
            "🧹 **/clear_channels** — Stop monitoring all channels\n"
            "🧹 **/clear_keywords** — Remove all keywords\n"
            "📊 **/status** — See what I am currently doing"
        )
        await event.reply(text)

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/status$"))
    async def cmd_status(event):
        active_ch = [c["name"] for c in ACTIVE_CONFIG["channels"] if c.get("enabled")]
        kws = ACTIVE_CONFIG["keywords"]
        
        text = f"📊 **Current Status**\n\n"
        text += f"**Monitoring {len(active_ch)} Channels:**\n"
        if active_ch:
            text += "\n".join(f"• {c}" for c in active_ch)
        else:
            text += "_None_"
            
        text += f"\n\n**Watching for {len(kws)} Keywords:**\n"
        text += ", ".join(kws) if kws else "_None_"
        
        await event.reply(text)

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/add_keyword (.*)"))
    async def cmd_add_keyword(event):
        kw = event.pattern_match.group(1).strip().lower()
        if kw in [k.lower() for k in ACTIVE_CONFIG["keywords"]]:
            await event.reply(f"⚠️ Keyword `{kw}` is already in the list.")
            return
            
        ACTIVE_CONFIG["keywords"].append(kw)
        await save_config(bot_client, user_id)
        await event.reply(f"✅ Added keyword: `{kw}`")

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/remove_keyword (.*)"))
    async def cmd_remove_keyword(event):
        kw = event.pattern_match.group(1).strip().lower()
        lower_kws = [k.lower() for k in ACTIVE_CONFIG["keywords"]]
        
        if kw in lower_kws:
            idx = lower_kws.index(kw)
            removed = ACTIVE_CONFIG["keywords"].pop(idx)
            await save_config(bot_client, user_id)
            await event.reply(f"✅ Removed keyword: `{removed}`")
        else:
            await event.reply(f"⚠️ Keyword `{kw}` not found.")

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/clear_keywords$"))
    async def cmd_clear_keywords(event):
        ACTIVE_CONFIG["keywords"] = []
        await save_config(bot_client, user_id)
        await event.reply("🧹 All keywords have been removed. Add new ones using `/add_keyword <word>`")

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/clear_channels$"))
    async def cmd_clear_channels(event):
        for ch in ACTIVE_CONFIG["channels"]:
            ch["enabled"] = False
        await save_config(bot_client, user_id)
        await event.reply("🧹 Stopped monitoring all channels. Use `/channels` to enable some.")

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/keywords$"))
    async def cmd_keywords(event):
        kws = ACTIVE_CONFIG["keywords"]
        if not kws:
            await event.reply("You have no keywords. Add one with `/add_keyword <word>`")
            return
        text = "**Current Keywords:**\n" + ", ".join(f"`{k}`" for k in kws)
        text += "\n\n_Use /add_keyword <word> or /remove_keyword <word> to edit._"
        await event.reply(text)

    # ── Channel Selector GUI ──────────────────────────────────────────────────
    
    def build_channel_buttons(page: int = 0):
        # We display 10 channels per page
        per_page = 10
        total_pages = max(1, (len(USER_CHANNELS) + per_page - 1) // per_page)
        page = max(0, min(page, total_pages - 1))
        
        start = page * per_page
        end = start + per_page
        page_channels = USER_CHANNELS[start:end]
        
        # Get active channel IDs
        active_ids = {c["id"] for c in ACTIVE_CONFIG["channels"] if c.get("enabled")}
        
        buttons = []
        for ch in page_channels:
            is_active = ch.id in active_ids
            emoji = "✅" if is_active else "❌"
            buttons.append([Button.inline(f"{emoji} {ch.name}", data=f"toggle_{ch.id}_{page}")])
            
        # Navigation row
        nav = []
        if page > 0:
            nav.append(Button.inline("⬅️ Prev", data=f"page_{page-1}"))
        nav.append(Button.inline(f"Page {page+1}/{total_pages}", data="ignore"))
        if page < total_pages - 1:
            nav.append(Button.inline("Next ➡️", data=f"page_{page+1}"))
            
        if nav:
            buttons.append(nav)
            
        return buttons

    @bot_client.on(events.NewMessage(chats=[user_id], pattern=r"^/channels$"))
    async def cmd_channels(event):
        if not USER_CHANNELS:
            await event.reply("Could not find any channels in your account.")
            return
            
        await event.reply(
            "📡 **Select Channels to Monitor**\nClick a button to toggle monitoring:",
            buttons=build_channel_buttons(0)
        )

    @bot_client.on(events.CallbackQuery())
    async def callback_handler(event):
        data = event.data.decode("utf-8")
        
        if data == "ignore":
            await event.answer()
            return
            
        if data.startswith("page_"):
            page = int(data.split("_")[1])
            await event.edit(buttons=build_channel_buttons(page))
            return
            
        if data.startswith("toggle_"):
            parts = data.split("_")
            ch_id = int(parts[1])
            page = int(parts[2])
            
            # Find the channel in config, or add it
            ch_config = next((c for c in ACTIVE_CONFIG["channels"] if c["id"] == ch_id), None)
            
            if ch_config:
                # Toggle
                ch_config["enabled"] = not ch_config["enabled"]
            else:
                # Add new
                ch_obj = next((c for c in USER_CHANNELS if c.id == ch_id), None)
                if ch_obj:
                    ACTIVE_CONFIG["channels"].append({
                        "id": ch_obj.id,
                        "name": ch_obj.name,
                        "enabled": True
                    })
            
            # Save and update UI
            await save_config(bot_client, user_id)
            await event.edit(buttons=build_channel_buttons(page))
            await event.answer("Saved!")

    # ── Run Forever (With Dummy Web Server for Free Cloud Hosts) ──────────────
    print(Fore.GREEN + "\nBot is online and ready!" + Style.RESET_ALL)
    print("Send /help to your bot in Telegram to get started.\n")
    
    # Render requires a web server to bind to the PORT environment variable
    # We create a simple HTTP server that returns "Bot is running!"
    from aiohttp import web
    async def health_check(request):
        return web.Response(text="Bot is running!")
    
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Dummy Web Server running on port {port} (for keep-alive pings)")
    
    await asyncio.gather(
        bot_client.run_until_disconnected(),
        user_client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
