from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CommandHandler, CallbackContext, Updater
from .config import Config
# You need your bot token from @BotFather
TOKEN= Config.TELEGRAM_BOT_TOKEN

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Open Voice Assistant", web_app={"url": "https://your-frontend-url.com"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Tap to launch the assistant:", reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    # Add more handlers as needed

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
