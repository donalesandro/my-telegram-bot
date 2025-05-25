from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    filters
)
import logging
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (лучше хранить в переменных окружения)
TOKEN = "8097253421:AAFYdM2NA5GhrqH9hn98V0WgIUG6X85UJZM"

# Данные о микрозаймах
LOANS = {
    "5000": [
        {"name": "Вебзайм", "url": "https://clck.ru/3MFDCC", "description": "Первый заем - 0%"},
        {"name": "ЗАЁМ.РУ", "url": "https://clck.ru/3MEjzA", "description": "Первый и шестой заём под 0%"},
        {"name": "OneClickMoney", "url": "https://clck.ru/3MFDFx", "description": "Быстро, удобно и безопасно"},
        {"name": "А Деньги", "url": "https://clck.ru/3MEk73", "description": "Для новых клиентов первые 7 дней пользования - бесплатно"}
    ],
    "10000": [
        {"name": "MoneyMan", "url": "https://clck.ru/3MFDJn", "description": "Возможность продления займа до четырех недель."},
        {"name": "ВашКредит", "url": "https://clck.ru/3MEkCR", "description": "Первый заём бесплатно!"},
        {"name": "Кекас.ру", "url": "https://clck.ru/3MFDLb", "description": "Первые три займа - бесплатно!"},
        {"name": "ЗаймиРуб", "url": "https://clck.ru/3MEkSk", "description": "0% для первичных заемщиков до 30 000 руб"}
    ],
    "30000": [
        {"name": "Небус", "url": "https://clck.ru/3MEkGV", "description": "До 100 000 ₽ под 0,48% в день."},
        {"name": "Boostra", "url": "https://clck.ru/3MFDN2", "description": "Деньги на карту через 15 минут."},
        {"name": "Лайм-Займ", "url": "https://clck.ru/3MFDQh", "description": "Быстрое решение по заявке, мгновенное зачисление."},
        {"name": "ОтличныеНаличные", "url": "https://clck.ru/3MEkh2", "description": "До 30 000 ₽ на 25 дней под 0.8% в день"}
    ]
}

# Данные о Кредитном докторе
CREDIT_DOCTOR = {
    "name": "Кредитный доктор от Совкомбанка",
    "url": "https://sovcombank.ru/credit-doctor",
    "description": "Бесплатный анализ кредитной истории и рекомендации",
    "options": [
        {"name": "Проверить кредитный рейтинг", "url": "https://clck.ru/3MEneE"},
        {"name": "Получить рекомендации", "url": "https://clck.ru/3MEneE"},
        {"name": "Подобрать продукты", "url": "https://clck.ru/3MEneE"}
    ]
}

# Главное меню
MAIN_MENU_KEYBOARD = [
    ["🔍 Проверить кредитную историю"],
    ["💰 Подобрать микрозайм"],
    ["🩺 Кредитный доктор"],
    ["ℹ️ Помощь"]
]

async def start(update: Update, context: CallbackContext) -> None:
    """Приветственное сообщение с кнопками"""
    if not update.message:
        return
        
    user = update.effective_user
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я - финансовый помощник.\n\n"
        "💰 Помогу получить Вам займ под 0% прямо сейчас - на Вашу карту.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    if not update.message:
        return
        
    text = update.message.text
    
    if text == "🔍 Проверить кредитную историю":
        await check_credit_history(update, context)
    elif text == "💰 Подобрать микрозайм":
        await show_loan_amounts(update, context)
    elif text == "🩺 Кредитный доктор":
        await show_credit_doctor(update, context)
    elif text == "ℹ️ Помощь":
        await show_help(update, context)
    else:
        await update.message.reply_text("Пожалуйста, используйте кнопки меню")

async def check_credit_history(update: Update, context: CallbackContext) -> None:
    """Проверка кредитной истории"""
    keyboard = [
        [InlineKeyboardButton("Кредистория", url="https://clck.ru/3MEjm5")],
        [InlineKeyboardButton("← Назад в меню", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 <b>Проверка кредитной истории</b>\n\n"
        "Вы можете бесплатно раз в год проверить свою кредитную историю "
        "в следующих бюро:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def show_loan_amounts(update: Update, context: CallbackContext) -> None:
    """Выбор суммы микрозайма"""
    keyboard = [
        [InlineKeyboardButton("До 5 000 ₽", callback_data='loan_5000')],
        [InlineKeyboardButton("До 10 000 ₽", callback_data='loan_10000')],
        [InlineKeyboardButton("До 30 000 ₽", callback_data='loan_30000')],
        [InlineKeyboardButton("← Назад в меню", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💰 <b>Выберите сумму микрозайма:</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def show_loans(update: Update, context: CallbackContext, amount: str) -> None:
    """Показать варианты займов для выбранной суммы"""
    query = update.callback_query
    await query.answer()
    
    loans_list = LOANS.get(amount, [])
    
    buttons = []
    for loan in loans_list:
        buttons.append([InlineKeyboardButton(
            f"{loan['name']} - {loan['description']}",
            url=loan['url']
        )])
    
    buttons.append([InlineKeyboardButton("← Выбрать другую сумму", callback_data='back_to_amounts')])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    text = f"🏦 <b>Варианты займов до {amount} ₽:</b>\n\n"
    text += "\n".join([f"• {loan['name']}: {loan['description']}" for loan in loans_list])
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def show_credit_doctor(update: Update, context: CallbackContext) -> None:
    """Меню Кредитного доктора"""
    keyboard = [
        [InlineKeyboardButton(option["name"], url=option["url"])]
        for option in CREDIT_DOCTOR["options"]
    ]
    keyboard.append([InlineKeyboardButton("← Назад в меню", callback_data='main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🩺 <b>{CREDIT_DOCTOR['name']}</b>\n\n"
        f"{CREDIT_DOCTOR['description']}\n\n"
        "Доступные опции:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def show_help(update: Update, context: CallbackContext) -> None:
    """Меню помощи"""
    keyboard = [[InlineKeyboardButton("← Назад в меню", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "ℹ️ <b>Помощь</b>\n\n"
        "Здесь вы можете:\n\n"
        "• Проверить кредитную историю\n"
        "• Подобрать микрозайм\n"
        "• Получить финансовые советы\n\n"
        "• Чтобы увеличить вероятность и скорость одобрения займа, оставьте анкеты сразу в нескольких компаниях\n\n"
        "Оценивайте свои финансовые возможности и риски. Изучите все условия кредита (займа)\n\n"
        "Просто используйте кнопки меню",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'main_menu':
        await start_with_keyboard(query, context)
    elif query.data == 'back_to_amounts':
        await show_loan_amounts_from_query(query, context)
    elif query.data.startswith('loan_'):
        amount = query.data.split('_')[1]
        await show_loans(update, context, amount)

async def start_with_keyboard(query: Update, context: CallbackContext) -> None:
    """Стартовое сообщение с клавиатурой для callback"""
    user = query.from_user
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    
    await query.edit_message_text(
        f"👋 Привет, {user.first_name}!\n"
        "Я - финансовый помощник. Выберите действие:"
    )
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="Используйте кнопки меню:",
        reply_markup=reply_markup
    )

async def show_loan_amounts_from_query(query: Update, context: CallbackContext) -> None:
    """Показать суммы займов для callback"""
    keyboard = [
        [InlineKeyboardButton("До 5 000 ₽", callback_data='loan_5000')],
        [InlineKeyboardButton("До 10 000 ₽", callback_data='loan_10000')],
        [InlineKeyboardButton("До 30 000 ₽", callback_data='loan_30000')],
        [InlineKeyboardButton("← Назад в меню", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💰 <b>Выберите сумму микрозайма:</b>",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

def main() -> None:
    """Запуск бота"""
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("Бот запущен!")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")

if __name__ == '__main__':
    main()