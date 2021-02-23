import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

from api.handlers.lists import list_created_handler, all_list_shown, show_all_list
from api.handlers.main import start, cancel, user_chose_handler
from api.handlers.list_items import list_item_changing, edit_list_items
from api.states import LIST_CREATED, EDIT_LIST_ITEMS, ALL_LIST_SHOWN, SHOW_ALL_LISTS, NEW_LIST_CREATION


class Runner:
    def __init__(self, token: str):
        self._token = token
        self._updater = Updater(token)

    def run(self):

        conv_handler = ConversationHandler(
            allow_reentry=True,
            entry_points=[
                CommandHandler('start', start),
                CallbackQueryHandler(user_chose_handler, pattern=f'^({NEW_LIST_CREATION}|{SHOW_ALL_LISTS})$')
            ],
            states={
                ALL_LIST_SHOWN: [CallbackQueryHandler(all_list_shown, pattern='^(del_list_|edit_list_).*')],
                LIST_CREATED: [MessageHandler(~Filters.command, list_created_handler)],
                EDIT_LIST_ITEMS: [
                    MessageHandler(~Filters.command, edit_list_items),
                    CallbackQueryHandler(list_item_changing, pattern='^(add_list_item_|del_list_item_|sub_list_item_).*')
                ]
            },
            fallbacks=[
                CommandHandler('start', start), CommandHandler('cancel', cancel),
                CommandHandler('l', show_all_list), CommandHandler('list', show_all_list)
            ]
        )

        self._updater.dispatcher.add_handler(conv_handler)
        self._updater.start_polling()
        self._updater.idle()


if __name__ == '__main__':
    BEETROOT_TG_TOKEN = os.environ['BEETROOT_TG_TOKEN']
    Runner(BEETROOT_TG_TOKEN).run()
