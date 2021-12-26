# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import re
from pprint import pprint

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

from model import Transaction

token = "2114958133:AAFCxSS4KHiLlf8Baq4PrL6g_fvfzfL7wT8"

regex = '^(Питание|Супермаркет|Здоровье/медицина|Дом|Транспорт|Личные расходы|Коммунальные услуги|Путешествия|Задолженности|Другое|Накопления|Связь|Еда вне дома|)$'

income_regex = '^(Сбережения|Зарплата|Премия|Процентный доход|Корзина|Категория 1)$'

AMOUNT, DESCRIPTION, CATEGORY = range(3)

INCOME_AMOUNT, INCOME_DESCRIPTION, INCOME_CATEGORY = range(3)


class CategoriesFilter(MessageFilter):
    def __init__(self, categories):
        self.categories = categories

    def filter(self, message):
        return message.text in self.categories


class ExpenseCategoriesFilter(CategoriesFilter):
    def __init__(self, categories):
        super().__init__(categories)


class IncomeCategoriesFilter(CategoriesFilter):
    def __init__(self, categories):
        super().__init__(categories)


transaction = Transaction()
incomeTransaction = Transaction()


def botSetup():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    expenseCategories = quickstart.loadExpenseCategories()
    expensesRegex = "^(" + "|".join(expenseCategories) + ")$"
    expenses_filter = ExpenseCategoriesFilter(expenseCategories)

    incomeCategories = quickstart.loadIncomeCategories()
    incomeRegex = "^(" + "|".join(incomeCategories) + ")$"
    income_filter = IncomeCategoriesFilter(incomeCategories)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('expense', expense)],
        states={
            AMOUNT: [MessageHandler(Filters.regex('^([0-9]+)$'), amount)],
            DESCRIPTION: [MessageHandler(Filters.text, description)],
            CATEGORY: [MessageHandler(expenses_filter, expenseCategory),
                       CallbackQueryHandler(expenseCategory, pattern=expensesRegex)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    income_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('income', income)],
        states={
            INCOME_AMOUNT: [MessageHandler(Filters.regex('^([0-9]+)$'), incomeAmount)],
            DESCRIPTION: [MessageHandler(Filters.text, incomeDescription)],
            CATEGORY: [MessageHandler(income_filter, incomeCategory),
                       CallbackQueryHandler(incomeCategory, pattern=incomeRegex)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(income_conv_handler)

    updater.start_polling()


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="bye")


def income(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сколько прилетело? 💸")

    return INCOME_AMOUNT


def incomeAmount(update, context):
    incomeTransaction.amount = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="За что такие деньги?")

    return INCOME_DESCRIPTION


def incomeDescription(update, context):
    incomeTransaction.description = update.message.text

    incomeCategories = quickstart.loadIncomeCategories()
    result = map(buttonFromCategory, incomeCategories)
    keyboard = list(result)

    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return INCOME_CATEGORY


def incomeCategory(update, context):
    pprint(update.callback_query.data)
    query = update.callback_query
    query.answer()

    incomeTransaction.category = query.data

    quickstart.insertIncome(incomeTransaction)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Получку записал, работаем дальше.")

    return ConversationHandler.END


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

    expenseCategories = quickstart.loadExpenseCategories()
    result = map(buttonFromCategory, expenseCategories)
    keyboard = list(result)

    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))

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

    quickstart.insertTransaction(transaction)

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
