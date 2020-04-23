from config import Config
from telebot import TeleBot
config_secrets = Config()


class TgBot:
    bot = TeleBot(config_secrets.tg_bot_key)
    events = []

    def __init__(self, events):
        self.events = events
        self.bot.polling()

    @bot.message_handler(func=lambda x: True)
    def start(mes, events=events):
        events.append({"text": mes.text})

if __name__ == "__main__":
    ar = []
    B = TgBot(ar)
