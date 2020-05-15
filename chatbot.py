"""Dieses Programm empfängt und sendet Informationen aus dem Telegram-chat des bots "prmatestbot". Der code kann für den
fertigen bot genau so verwendet werden, es muss lediglich das token an den neuen bot angepasst werden."""


from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters)
import logging


updater = Updater(token="1157696049:AAG_ih1xmSQGEckJkAVpHZrGLxbjR9hxOHM", use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="What's up, nerds?")


starthandler = CommandHandler("start", start)
dispatcher.add_handler(starthandler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


echohandler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echohandler)

updater.start_polling()
