from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Your bot token (from BotFather)
BOT_TOKEN = "7665533003:AAFFiM9qeQIYbU4Q8b50_BiKmAlHI6b9vX8"
# Channel ID (public -> "@channelusername", private -> numeric ID starting with -100)
CHANNEL_ID = "@femboy_house69"

# Store user_id : username mapping
usernames = {}

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me any message and I’ll post it in the channel.\n"
        "You can also set a nickname with /setusername <your_name>."
    )

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usage: /setusername <your_name>")
        return

    username = " ".join(context.args)
    user_id = update.message.from_user.id
    usernames[user_id] = username

    await update.message.reply_text(f"✅ Username set to: {username}")

# --- Forwarding Handler ---
async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = usernames.get(user_id, update.message.from_user.first_name)

    # Format message as "username: text"
    if update.message.text:
        msg = f"📝 {username}:\n{update.message.text}"
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    elif update.message.photo:
        # If it's a photo, send with caption
        caption = f"📸 {username}"
        if update.message.caption:
            caption += f":\n{update.message.caption}"

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption
        )
    else:
        await update.message.reply_text("⚠️ Sorry, only text and photos supported for now.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setusername", set_username))

    # Handle all messages
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_channel))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
