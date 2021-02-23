from typing import Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import callbackcontext

from api.states import LIST_CREATED, EDIT_LIST_ITEMS, ALL_LIST_SHOWN
from api.loggers import logger
from api.db.storage import Storage
from api.handlers.list_items import list_item_changing


def new_list_creation(update: update.Update, context: callbackcontext.CallbackContext):
    query = update.callback_query
    query.answer()

    query.message.reply_text('Введите название списка')
    return LIST_CREATED


def list_created_handler(update: update.Update, context: callbackcontext.CallbackContext):
    context.user_data['current_list_name'] = update.message.text
    try:
        Storage.create_good_list(context.user_data['user_id'], update.message.text)
    except Exception as e:
        # TODO catch ListAlreadyExists and show proper message
        logger.error(e, exc_info=True)

    update.message.reply_text(
        text='Введите первый элемент списка'
    )
    return EDIT_LIST_ITEMS


def show_all_list(update: update.Update, context: callbackcontext.CallbackContext):
    user_id = context.user_data['user_id']
    reply_markup, count = _get_lists_markupkeyboard(user_id)

    query = update.callback_query
    if query:
        query.answer()
        query.message.edit_text(
            text='Все списки' if count else 'Список пуст, создайте новый: /start',
            reply_markup=reply_markup
        )
    else:
        update.message.reply_markdown(
            text='Все списки' if count else 'Список пуст, создайте новый: /start',
            reply_markup=reply_markup
        )
    return ALL_LIST_SHOWN


def all_list_shown(update: update.Update, context: callbackcontext.CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = context.user_data['user_id']

    if 'del_list_' in query.data:
        # Pressed remove list button
        list_name_to_remove = query.data[query.data.index('del_list_') + 9:]
        if list_name_to_remove:
            Storage.delete_list(user_id, list_name_to_remove)
            markup, users_lists_cnt = _get_lists_markupkeyboard(user_id)
            if users_lists_cnt:
                query.message.edit_reply_markup(
                        reply_markup=markup,
                )
            else:
                query.message.reply_text(text='Список пуст, создайте новый: /start')

    else:
        # Pressed on specifig list
        list_name = query.data[query.data.index('edit_list_') + 10:]
        context.user_data['current_list_name'] = list_name
        return list_item_changing(update, context)


def _get_lists_markupkeyboard(user_id) -> Tuple[InlineKeyboardMarkup, int]:
    keyboard = []

    users_lists = Storage.all_list(user_id)
    for item in users_lists:
        row = list()
        row.append(InlineKeyboardButton(item.name, callback_data=f'edit_list_{item.name}'))
        for btn_text, btn_callback_suffix in [('remove', 'del_list')]:
            row.append(InlineKeyboardButton(btn_text, callback_data=f'{btn_callback_suffix}_{item.name}'))
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard), len(users_lists)
