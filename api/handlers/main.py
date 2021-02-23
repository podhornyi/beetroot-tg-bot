from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import callbackcontext

from api.states import SHOW_ALL_LISTS, NEW_LIST_CREATION
from api.loggers import logger
from telegram.ext import ConversationHandler
from api.handlers.lists import new_list_creation, show_all_list


def start(update: update.Update, context: callbackcontext.CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Все списки", callback_data=str(SHOW_ALL_LISTS))],
        [InlineKeyboardButton("Добавить новый список", callback_data=str(NEW_LIST_CREATION))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text='Выбери свой путь',
        reply_markup=reply_markup
    )


def cancel(update: update.Update, context: callbackcontext.CallbackContext):
    update.message.reply_text(text='Очень жаль, /start')
    return ConversationHandler.END


def user_chose_handler(update: update.Update, context: callbackcontext.CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data['user_id'] = query.from_user.id

    try:
        if int(query.data) == NEW_LIST_CREATION:
            return new_list_creation(update, context)

        if int(query.data) == SHOW_ALL_LISTS:
            return show_all_list(update, context)
    except ValueError:
        logger.error(f'Cant parse to int: {query.data}')
