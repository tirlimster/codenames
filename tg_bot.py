from config import Config
from threading import Thread
from telebot import TeleBot
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


if __name__ == "__main__":
    ar = []
    BOT = TgBot(ar)
    t1 = Thread(target=BOT.mainloop)
    t1.start()
    while True:
        print(ar)
        sleep(1)
