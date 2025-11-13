import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from PIL import Image, ImageOps

# ==============================
# Environment setup
# ==============================
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8443"))
DOMAIN = os.getenv("RAILWAY_STATIC_URL") or "https://tpa-affiliate-bot.up.railway.app"

# ==============================
# Game partners
# ==============================
GAMES = {
    "IPAY9": {"url": "https://ipay9aud.com", "bonus": "🎁 Welcome Bonus 100%", "group": "https://t.me/ipay9aus"},
    "SPONGEBOB13": {"url": "https://spongebob13.net", "bonus": "🔥 Free Credit AUD103.33", "group": "https://t.me/Spongebob13ChannelAus"},
    "WINNIE13": {"url": "https://winnie13.net", "bonus": "💎 Free Credit AUD103.33", "group": "https://t.me/winie13_13"},
    "MICKY13": {"url": "https://www.micky13.net", "bonus": "💰 Daily Bonus AUD9", "group": "https://t.me/micky13_au"},
    "BK9": {"url": "https://bk9aus.com", "bonus": "⚡️ Daily Easy Step Free AUD100", "group": "https://t.me/bk9aus"},
    "ROLEX9": {"url": "https://rolex9.net", "bonus": "🧧 Free Credit AUD99.99", "group": "https://t.me/rolex9au"},
    "KINGBET9": {"url": "https://kingbet9aus.com", "bonus": "🌟 Free Credit AUD99.99", "group": "https://t.me/KINGBET9AUD"},
    "ME99": {"url": "https://me99aud.com", "bonus": "🎯 New Free 365 Days Bonus", "group": "https://t.me/me99ausgroup"},
    "BYBID9": {"url": "https://bybid9.com", "bonus": "💎 Daily First Deposit 30%", "group": "https://t.me/bybid9auvipp"},
    "MRBEAN9": {"url": "https://mrbean9.com", "bonus": "🚀 Free Credit AUD99.99", "group": "https://t.me/mrbean9Au"},
    "QUEEN13": {"url": "https://queen13.net", "bonus": "🎰 Registration Free AUD113", "group": "https://t.me/queen13aus13"},
    "GUCCI9": {"url": "https://gucci9.vip", "bonus": "💵 Free Credit AUD109.99", "group": "https://t.me/guccii_9"},
    "BP77": {"url": "https://bigpay77.net", "bonus": "🔥 Free Credit AUD77.77", "group": "https://t.me/BIGPAY77"},
}


# ==============================
# Image padding helper
# ==============================
def pad_image(image_path):
    img = Image.open(image_path)
    desired_ratio = 1.91
    w, h = img.size
    current_ratio = w / h
    if current_ratio < desired_ratio:
        new_w = int(h * desired_ratio)
        padding = (new_w - w) // 2
        img = ImageOps.expand(img, border=(padding, 0, padding, 0), fill="white")
    elif current_ratio > desired_ratio:
        new_h = int(w / desired_ratio)
        padding = (new_h - h) // 2
        img = ImageOps.expand(img, border=(0, padding, 0, padding), fill="white")
    return img


# ==============================
# /status
# ==============================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is online and webhook is active!")


# ==============================
# /start welcome
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "Player"
    photo_path = "main_env/images/tpa-authorize-no-bg.png"

    caption = (
        f"G’day! Welcome {name},\n\n"
        "「✔ ᵛᵉʳᶦᶠᶦᵉᵈ」\n"
        "💎 TPA – Trusted Pokies Australia\n\n"
        "Licensed 🔰 | Verified ✅ | Integrity 🤝\n\n"
        "Tap below to explore certified partners or claim bonuses 👇"
    )

    keyboard = [
        [InlineKeyboardButton("🟢 View All Certified Platforms", callback_data="show_all")],
        [InlineKeyboardButton("🎁 Get Secret Room Bonus", callback_data="secret_room")],
        [InlineKeyboardButton("🌐 TPA Affiliate Network", url="https://heylink.me/tpaaustralia/")],
    ]

    with open(photo_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


# ==============================
# Callback: show all partners
# ==============================
async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    caption = "Here are all TPA certified partners 👇"
    buttons = [
        [InlineKeyboardButton(f"{name} — {info['bonus']}", callback_data=f"detail_{name}")]
        for name, info in GAMES.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="go_back")])
    await query.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(buttons))


# ==============================
# Callback: secret room
# ==============================
async def secret_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    caption = "🎁 *Exclusive Secret Room Bonus Links*"
    buttons = [[InlineKeyboardButton(f"{n} Group", url=i["group"])] for n, i in GAMES.items()]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="go_back")])
    await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


# ==============================
# Callback: show detail
# ==============================
async def show_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    company = query.data.replace("detail_", "")
    info = GAMES[company]
    caption = f"🔥 *{company}*\n\nBonus: {info['bonus']}\n\nTry this platform?"
    buttons = [
        [InlineKeyboardButton(f"✅ Yes, Go to {company}", callback_data=f"visit_{company}")],
        [InlineKeyboardButton("🔁 Back", callback_data="show_all")],
    ]
    await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


# ==============================
# Callback: visit
# ==============================
async def visit_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    company = query.data.replace("visit_", "")
    info = GAMES[company]
    await query.message.reply_text(
        f"✅ Verified link opened.\n👉 [Open {company}]({info['url']})",
        parse_mode="Markdown",
    )


# ==============================
# Callback: go_back
# ==============================
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)


# ==============================
# Main Entry
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(show_all, pattern="^show_all$"))
    app.add_handler(CallbackQueryHandler(secret_room, pattern="^secret_room$"))
    app.add_handler(CallbackQueryHandler(show_detail, pattern="^detail_"))
    app.add_handler(CallbackQueryHandler(visit_platform, pattern="^visit_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))

    print("✅ TPA Affiliate Bot is running with Webhook...")
    print(f"🌐 Webhook URL: {DOMAIN}/{TOKEN}")
    print(f"📡 Listening on port {PORT}")

    # 🔹 关键差异：不使用 asyncio.run()，直接 run_webhook()
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{DOMAIN}/{TOKEN}",
    )
