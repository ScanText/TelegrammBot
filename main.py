import logging
from telegram.request import HTTPXRequest
import requests
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "7921017073:AAGzWWL-v46dTtNLoAu2N9dK_gtw0554q18"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

EXTRACT_TEXT_URL = "https://fastapitext.fly.dev/extract-text/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Загрузить фотографию", callback_data="upload_photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "👋 Привет! Этот бот позволяет извлекать текст с изображений.\n\n"
        "📷 Просто отправь фотографию с текстом, и я пришлю тебе результат.\n"
        "🔁 После каждой обработки ты сможешь загрузить следующую фотографию.\n\n"
        "⚠️ *Важно:* бот работает только с изображениями, содержащими *английский текст*."
    )
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "upload_photo":
        await query.edit_message_text("📸 Пожалуйста, пришли мне фотографию.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = await photo_file.download_to_drive()

    await update.message.reply_text("🔄 Извлекаю текст...")

    with open(file_path.name, "rb") as f:
        files = {"file": ("image.jpg", f, "image/jpeg")}
        try:
            response = requests.post(EXTRACT_TEXT_URL, files=files)
            if response.status_code == 200:
                data = response.json()
                text = data.get("text", "").strip()
                if text:
                    await update.message.reply_text(f"📄 Извлечённый текст:\n\n{text}")
                else:
                    await update.message.reply_text("❗️ Текст не найден на изображении.")
            else:
                await update.message.reply_text("⚠️ Ошибка при обращении к API.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")

    keyboard = [
        [InlineKeyboardButton("📸 Загрузить следующую фотографию", callback_data="upload_photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что дальше?", reply_markup=reply_markup)


def main():
    app = ApplicationBuilder().token("7921017073:AAGzWWL-v46dTtNLoAu2N9dK_gtw0554q18").request(HTTPXRequest()).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
