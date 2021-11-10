# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import re
import quickstart

from typing import List, Union

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    MessageFilter, CallbackQueryHandler
)

token = "2114958133:AAFCxSS4KHiLlf8Baq4PrL6g_fvfzfL7wT8"

regex = '^(Питание|Супермаркет|Здоровье/медицина|Дом|Транспорт|Личные расходы|Коммунальные услуги|Путешествия|Задолженности|Другое|Накопления|Связь|Еда вне дома|)$'

AMOUNT, DESCRIPTION, CATEGORY = range(3)

EXPENSE_CATEGORIES = ['Питание', 'Супермаркет', 'Здоровье/медицина', 'Дом', 'Транспорт', 'Личные расходы',
                      'Коммунальные услуги', 'Путешествия', 'Задолженности', 'Другое', 'Накопления', 'Связь',
                      'Еда вне дома']


class Transaction:
    amount = 0
    description = ""
    category = EXPENSE_CATEGORIES[0]


class ExpenseCategoriesFilter(MessageFilter):
    def filter(self, message):
        return message.text in EXPENSE_CATEGORIES


transaction = Transaction()


def botSetup():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    expenses_filter = ExpenseCategoriesFilter()

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('expense', expense)],
        states={
            AMOUNT: [MessageHandler(Filters.regex('^([0-9]+)$'), amount)],
            DESCRIPTION: [MessageHandler(Filters.text, description)],
            CATEGORY: [MessageHandler(expenses_filter, expenseCategory),
                       CallbackQueryHandler(expenseCategory, pattern=regex)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="bye")


def expense(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сколько шекелей заплатил? 🪙")

    return AMOUNT


def amount(update, context):
    transaction.amount = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Такс, понятно, а на что?")

    return DESCRIPTION


def description(update, context):
    """Sends a message with three inline buttons attached."""
    transaction.description = update.message.text

    result = map(buttonFromCategory, EXPENSE_CATEGORIES)
    keyboard = list(result)

    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=1))

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return CATEGORY


def build_menu(
        buttons: List[InlineKeyboardButton],
        n_cols: int,
        header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None,
        footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]] = None
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return menu


def buttonFromCategory(category):
    return InlineKeyboardButton(category, callback_data=category)


def expenseCategory(update, context):
    query = update.callback_query
    query.answer()

    transaction.category = query.data

    quickstart.insertTransaction(transaction.amount, transaction.description, transaction.category)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Взяли на карандашик, беги дальше. Кабанчик. <3")

    return ConversationHandler.END


def start(update, context):
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    botSetup()

# See PyCharm help at https://www.jetbrains.com/help/pycharm
