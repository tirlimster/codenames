from config import Config
from threading import Thread
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup as tgMarkup
from telebot.types import InlineKeyboardButton as tgButton
from time import sleep
config_secrets = Config()

class TgBot:
    bot = TeleBot(config_secrets.tg_bot_key)
    events = []

    def __init__(self, events):
        self.events.append(events)

    def main_loop(self):
        self.bot.polling()

    def show(self):
        print(self.events[0])

    @bot.message_handler(func=lambda x: True)
    def parse_message(mes, events=events):
        events[0].append({
            "text": mes.text,
            "first": mes.from_user.first_name,
            "last": mes.from_user.last_name,
            "id": mes.from_user.id,
            "platform": "tg"
        })

    @bot.callback_query_handler(func=lambda x: True)
    def parse_callback(call, events=events, bot=bot):
        events[0].append({
            "text": call.data,
            "first": call.from_user.first_name,
            "last": call.from_user.last_name,
            "id": call.from_user.id,
            "platform": "tg"
        })
        bot.answer_callback_query(call.id, "Chosen word: " + call.data)


    def write_message(self, player_id, text, buttons=None):
        markup = tgMarkup()
        markup.row_width = 5
        th = u'\U0001F4A8'
        markup.add(tgButton('th', callback_data="word"))
        self.bot.send_message(player_id, th, reply_markup=markup)


if __name__ == "__main__":
    ar = []
    BOT = TgBot(ar)
    t1 = Thread(target=BOT.main_loop)
    BOT.write_message(406323156, "Hello")
    t1.start()
    while True:
        sleep(1)
