import os
import sqlite3
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from PIL import Image, ImageOps

TOKEN = os.getenv("BOT_TOKEN")

# ==============================
# 用户统计数据库（fly.io volume）
# ==============================
DB_PATH = "/data/users.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    first_seen TEXT,
    last_seen TEXT
)
""")
conn.commit()

def save_user(user):
    now = datetime.utcnow().isoformat()
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
    exists = cur.fetchone()
    if exists:
        cur.execute("UPDATE users SET last_seen=? WHERE user_id=?", (now, user.id))
    else:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                    (user.id, user.username, user.first_name, user.last_name, now, now))
    conn.commit()

# ==============================
#  所有认证游戏平台 + Telegram 群组
# ==============================
GAMES = {
    "IPAY9": {"url": "https://ipay9aud.com/register/SMSRegister", "bonus": "🎁 Daily Easy Step Free $100", "group": "https://t.me/ipay9aus"},
    "KINGBET9": {"url": "https://www.kingbet9aus.bet/register/SMSRegister", "bonus": "🌟 Register Free Credit $110", "group": "https://t.me/KINGBET9AUD"},
    "BP77": {"url": "https://bigpay77.net/register/SMSRegister", "bonus": "🔥 New Register Free $187.77", "group": "https://t.me/BIGPAY77"},
    "ME99": {"url": "https://me99aud.com/register/SMSRegister", "bonus": "🎯 Free Credit Bonus $109.99", "group": "https://t.me/me99aus"},
    "ROLEX9": {"url": "https://rolex9.net/register/SMSRegister", "bonus": "💰 Free Credit $129.99", "group": "https://t.me/rolex9au"},
    "GUCCI9": {"url": "https://gucci9au.net/register/SMSRegister", "bonus": "💵 Daily Easy Bonus $100", "group": "https://t.me/guccii_9"},
    "QUEEN13": {"url": "https://www.queen13.net/register/SMSRegister", "bonus": "🎰 New Registration Free $113", "group": "https://t.me/queen13aus13"},
    "BYBID9": {"url": "https://bybid9.com/register/SMSRegister", "bonus": "💥 Exclusive Grand Jackpot $5088", "group": "https://t.me/bybid9auvipp"},
    "MICKY9": {"url": "https://micky13.net/register/SMSRegister", "bonus": "💰 Free Credit $103.33", "group": "https://t.me/micky13_au"},
    "WINNIE777": {"url": "https://www.winnie13.net/register/SMSRegister", "bonus": "💎 Free Credit $113.33", "group": "https://t.me/winie13_13"},
    "MRBEAN9": {"url": "https://www.mrbean9.com/register/SMSRegister", "bonus": "🚀 Register Free $199.99", "group": "https://t.me/mrbean9Au"},
    "POKEMON9": {"url": "https://pkm9aus.com/register/SMSRegister", "bonus": "💰 Free Credit $109.99", "group": "https://t.me/pokemon13channel"},
}

# ==============================
# 共用函数：自动修正图片比例
# ==============================
def pad_image(image_path):
    img = Image.open(image_path)
    desired_ratio = 1.91
    w, h = img.size
    current_ratio = w / h
    if current_ratio < desired_ratio:
        new_w = int(h * desired_ratio)
        padding = (new_w - w) // 2
        img = ImageOps.expand(img, border=(padding, 0, padding, 0), fill='white')
    elif current_ratio > desired_ratio:
        new_h = int(w / desired_ratio)
        padding = (new_h - h) // 2
        img = ImageOps.expand(img, border=(0, padding, 0, padding), fill='white')
    return img


# ==============================
# Step 1 欢迎页
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    name = user.first_name or user.username or "Player"
    photo_path = "main_env/images/tpa-authorize.png"

    caption = (
        f"G’day! Welcome {name}, \n\n"
        "「✔ ᵛᵉʳᶦᶠᶦᵉᵈ」\n"
        "You’re now connected with \n"
        "💎 TPA – Trusted Pokies Australia \n\n"
        "Licensed 🔰 | Verified ✅ | Integrity 🤝 \n\n"
        "Tap below to explore certified partners or claim secret bonuses 👇"
    )

    keyboard = [
        [InlineKeyboardButton("🟢 View Certified Platforms", callback_data="show_all")],
        [InlineKeyboardButton("🎁 Limited Secret Room Bonus", callback_data="secret_room")],
        [
            InlineKeyboardButton("🔗 TPA Affiliate Network", url="https://heylink.me/tpaaustralia/"),
            InlineKeyboardButton("🌐 TPA Official Authority", url="https://www.tpaofficial.com/")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass

    with open(photo_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    context.user_data["last_action"] = "home"


# ==============================
# /stats 查看用户数
# ==============================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    await update.message.reply_text(f"📊 Total users started bot: {total}")


# ==============================
# Step 2 显示所有公司
# ==============================
async def show_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    caption = "Here are all TPA certified partners 👇\n\nTap a brand to see its bonus offer:"
    buttons = [
        [InlineKeyboardButton(f"{name} — {info['bonus']}", callback_data=f"detail_{name}")]
        for name, info in GAMES.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="go_back")])

    await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    context.user_data["last_action"] = "show_all"


# ==============================
# Step 3 Secret Room Bonus List
# ==============================
async def secret_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    caption = "🎁 *Exclusive Secret Room Bonus Links*\n\nJoin the official Telegram groups of our certified partners 👇"
    buttons = [
        [InlineKeyboardButton(f"{name} ✈️ Telegram Group", url=info["group"])]
        for name, info in GAMES.items()
    ]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="go_back")])

    await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    context.user_data["last_action"] = "secret_room"


# ==============================
# Step 4 显示公司详情
# ==============================
async def show_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    company_name = query.data.replace("detail_", "")
    await show_detail_for_company(query, context, company_name)


async def show_detail_for_company(query, context, company_name):
    info = GAMES[company_name]
    image_path = "main_env/images/tpa-authorize.png"

    caption = (
        f"🔥 *{company_name}* is one of our verified partners!\n\n"
        f"Bonus Offer: {info['bonus']}\n\n"
        "Would you like to try this platform or explore other promotions?"
    )

    buttons = [
        [InlineKeyboardButton(f"✅ Yes, Go to {company_name}", callback_data=f"visit_{company_name}")],
        [InlineKeyboardButton("🔁 Show other promotions", callback_data="show_all")],
    ]

    try:
        with open(image_path, "rb") as photo:
            await query.edit_message_media(
                media=InputMediaPhoto(media=photo, caption=caption, parse_mode="Markdown"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except FileNotFoundError:
        await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    context.user_data["last_action"] = f"detail_{company_name}"


# ==============================
# Step 5 跳转官网 + 自动回复确认
# ==============================
async def visit_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    company_name = query.data.replace("visit_", "")
    info = GAMES[company_name]
    await query.answer(f"Opening {company_name}... 🚀", show_alert=False)

    msg = await query.message.reply_text(
        f"✅ You’ve accessed via TPA verified link.\n🎰 Enjoy your bonus and play safe! \n\n"
        f"👉 [Register Now - {company_name}]({info['url']})",
        parse_mode="Markdown"
    )
    context.user_data["last_verified_msg"] = msg.message_id
    context.user_data["last_action"] = f"visit_{company_name}"


# ==============================
# Step 6 返回上一层（动态）
# ==============================
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    last_action = context.user_data.get("last_action")

    if not last_action or last_action == "home":
        await start(update, context)
        return

    if last_action == "show_all" or last_action == "secret_room":
        await start(update, context)
        context.user_data["last_action"] = "home"
        return

    if last_action.startswith("detail_"):
        await show_all(update, context)
        context.user_data["last_action"] = "show_all"
        return

    if last_action.startswith("visit_"):
        company_name = last_action.replace("visit_", "")
        await show_detail_for_company(query, context, company_name)
        return


# ==============================
# 主程序入口
# ==============================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(show_all, pattern="^show_all$"))
    app.add_handler(CallbackQueryHandler(secret_room, pattern="^secret_room$"))
    app.add_handler(CallbackQueryHandler(show_detail, pattern="^detail_"))
    app.add_handler(CallbackQueryHandler(visit_platform, pattern="^visit_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    print("✅ TPA Affiliate Bot is running...")
    app.run_polling(close_loop=False)

