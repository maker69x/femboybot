import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7665533003:AAFFiM9qeQIYbU4Q8b50_BiKmAlHI6b9vX8"
CHANNEL_ID = "@femboy_house69"

# --- Database setup ---
conn = sqlite3.connect("usernames.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS usernames (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE
)
""")
conn.commit()

# --- Helper Functions ---
def set_username_db(user_id: int, username: str) -> bool:
    try:
        cursor.execute("INSERT OR REPLACE INTO usernames (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_username_db(user_id: int):
    cursor.execute("SELECT username FROM usernames WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def is_username_taken(username: str, user_id: int) -> bool:
    cursor.execute("SELECT user_id FROM usernames WHERE username = ?", (username,))
    row = cursor.fetchone()
    return row and row[0] != user_id

def delete_username_db(user_id: int):
    cursor.execute("DELETE FROM usernames WHERE user_id = ?", (user_id,))
    conn.commit()

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Set your nickname with /setusername <name>.\n"
        "If you change it, your old name will be freed for others."
    )

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("❗ Usage: /setusername <your_name>")
        return

    new_username = " ".join(context.args)

    # Check if taken
    if is_username_taken(new_username, user_id):
        await update.message.reply_text("🚫 This username is already taken. Try another.")
        return

    # Free old username
    delete_username_db(user_id)

    # Assign new one
    set_username_db(user_id, new_username)
    await update.message.reply_text(f"✅ Your username is now: {new_username}")

async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = get_username_db(user_id) or update.message.from_user.first_name

    if update.message.text:
        msg = f"📝 {username}:\n{update.message.text}"
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)

    elif update.message.photo:
        caption = f"📸 {username}"
        if update.message.caption:
            caption += f":\n{update.message.caption}"

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption
        )

    else:
        await update.message.reply_text("⚠️ Only text & photos supported right now.")

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setusername", set_username))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_channel))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
