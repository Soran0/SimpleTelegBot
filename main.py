import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
import logging
import csv
import datetime as dt

TOKEN = os.environ.get('TOKEN')

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Состояния пользователей
user_states = {}
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Инлайн-кнопки
    inline_keyboard = [
        [InlineKeyboardButton('Aliexpress', callback_data='url_ali')],
        [InlineKeyboardButton('Send me your URL', callback_data='send_url')]
    ]
    reply_markup_inline = InlineKeyboardMarkup(inline_keyboard)

    # Reply-кнопки
    reply_keyboard = [['My saved data'], ['Help']]
    reply_markup_reply = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Отправляем сообщение с инлайн-кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an option:", reply_markup=reply_markup_inline)

    # Отправляем сообщение с reply-кнопками
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an action:", reply_markup=reply_markup_reply)

# Обработка нажатий на инлайн-кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Отвечаем на нажатие кнопки

    user_id = query.from_user.id

    if query.data == 'send_url':
        user_states[user_id] = 'awaiting_url'
        await context.bot.send_message(chat_id=query.message.chat.id, text="Please send me the URL.")
    elif query.data == 'url_ali':
        await context.bot.send_message(chat_id=query.message.chat.id, text='https://www.aliexpress.com')
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text=f'You selected: {query.data}')

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == 'My saved data':
        with open('user_data.csv', mode='r') as file:
            await update.message.reply_text(f"Your saved data:")
            for item in file:
                await update.message.reply_text(item)


    elif user_states.get(user_id) == 'awaiting_url':
        user_data[user_id] = text
        await update.message.reply_text(f"URL saved: {text}")
        with open('user_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([dt.datetime.now().strftime('%Y-%m-%d'), update.message.text])

        user_states[user_id] = None
    elif text == 'Help':
        await update.message.reply_text('I`m here to help you with your shopping.')
    else:
        await update.message.reply_text("Please choose an option or send a URL.")

if __name__ == '__main__':
    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд и сообщений
    start_handler = CommandHandler('start', start)
    button_handler = CallbackQueryHandler(button)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

    # Добавляем обработчики
    application.add_handler(start_handler)
    application.add_handler(button_handler)
    application.add_handler(message_handler)

    # Запускаем бота
    application.run_polling()