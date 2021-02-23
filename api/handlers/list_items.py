import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import callbackcontext

from api.states import EDIT_LIST_ITEMS
from api.loggers import logger
from api.db.storage import Storage
from api.exceptions import GoodInListAlreadyExistsError, ListNotExistsError


def list_item_changing(update: update.Update, context: callbackcontext.CallbackContext):
    query = update.callback_query
    query.answer()

    current_list_name, user_id = context.user_data['current_list_name'], context.user_data['user_id']
    text = f'Список "{current_list_name}"'
    if 'edit_list_' not in query.data:
        matcher = re.compile('^(add_list_item_|del_list_item_|sub_list_item_)')
        data = list(filter(lambda item: item != '', matcher.split(query.data)))

        if len(data) != 2:
            # TODO: no callback provided or action/item not splitted correctly
            logger.info(f'query.data={query.data}, data={data}')
            return EDIT_LIST_ITEMS

        action = data[0]
        item_name = data[1]

        if action == 'del_list_item_':
            Storage.delete_item(user_id, current_list_name, item_name)
        elif action == 'sub_list_item_':
            Storage.substract_item_qtty(user_id, current_list_name, item_name)
        elif action == 'add_list_item_':
            Storage.add_item_qtty(user_id, current_list_name, item_name)

    query.message.edit_text(
        text=text,
        reply_markup=_get_list_items_markupkeyboard(context)
    )
    return EDIT_LIST_ITEMS


def edit_list_items(update: update.Update, context: callbackcontext.CallbackContext):
    current_list_name = context.user_data.get('current_list_name')
    if not current_list_name:
        logger.info(f'current_list_name is empty')
        return

    update.message.reply_text(
        text=f'Список "{current_list_name}"',
        reply_markup=_get_list_items_markupkeyboard(context, update.message.text)
    )


def _get_list_items_markupkeyboard(context: callbackcontext.CallbackContext, new_item_name: str = None) -> InlineKeyboardMarkup:
    user_id = context.user_data['user_id']
    current_list_name = context.user_data['current_list_name']
    if new_item_name:
        try:
            Storage.add_new_item(
                user_id,
                new_item_name,
                current_list_name,
            )
        except GoodInListAlreadyExistsError:
            logger.error(f'{new_item_name} already exists in list "{current_list_name}"')
        except ListNotExistsError:
            logger.error(f'"{current_list_name}" does not exists')

    keyboard = []
    for item in Storage.all_goods_in_list(user_id, current_list_name):
        row = list()
        row.append(InlineKeyboardButton(item.name, callback_data='test'))
        row.append(InlineKeyboardButton(str(item.qtty), callback_data='test'))
        for btn_text, btn_callback_suffix in [('-', 'sub_list_item'), ('+', 'add_list_item'), ('remove', 'del_list_item')]:
            row.append(InlineKeyboardButton(btn_text, callback_data=f'{btn_callback_suffix}_{item.name}'))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
