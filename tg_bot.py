from config import Config
from threading import Thread
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup as tgMarkup
from telebot.types import KeyboardButton as tgButton
from time import sleep

# only for tests
from generator import Board

config_secrets = Config()


class TgBot:
    def __init__(self, events):
        self.bot = TeleBot(config_secrets.tg_bot_key)
        self.events = events

    def listener(self, messages):
        for mes in messages:
            self.events.append({
                "text": mes.text,
                "first": mes.from_user.first_name,
                "last": mes.from_user.last_name,
                "id": str(mes.from_user.id),
                "platform": "tg"
            })

    def main_loop(self):
        self.bot.set_update_listener(self.listener)
        self.bot.polling()

    @staticmethod
    def parse_row(row):
        # mark_by_type = ["", "(ничье)", "(синие)", "(красное)", "(бомба!)"]
        mark_by_type = ["⬜", "🟦", "🟥", "⬛"]
        # mark_by_type = ["", "нич", "син", "кра", "бом"]
        # open_by_type = ["", "открыто"]
        markup_row = []
        for but in row:
            if type(but) == str:
                markup_row.append(tgButton(but.capitalize()))
            elif but[1]:
                markup_row.append(tgButton(f"{but[2].capitalize()}\n{mark_by_type[but[0]]}"))
            else:
                markup_row.append(tgButton(f"{but[2].upper()}"))
        return markup_row

    def write_message(self, player_id, text, buttons=None):
        markup = None
        if buttons is not None:
            markup = tgMarkup(row_width=5, resize_keyboard=True)
            for row in buttons:
                markup.add(*self.parse_row(row))
        self.bot.send_message(player_id, text, reply_markup=markup, parse_mode='markdown')


if __name__ == "__main__":
    ar = []
    BOT = TgBot(ar)
    t1 = Thread(target=BOT.main_loop)
    t1.start()
    while True:
        print(ar)
        while len(ar):
            board = Board(None)
            board.restart()
            BOT.write_message(ar[-1]["id"], "Вот слова", [["Главное меню"]] + board.showCaptain())
            ar.pop()
        sleep(1)
