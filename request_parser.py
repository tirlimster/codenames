import time
import threading
from database import Database
from vk_bot import VkBot


class Request:
    class Player:
        def __init__(self, player_id, db, bots):
            self.db = db
            data = self.db.get_player(player_id)
            if data is None:
                data = self.db.insert_player(player_id)
            self.player_id = data[0]
            self.current_admin = data[1]
            self.status = data[2]

            self.id = data[0][2:]
            self.bot = bots[data[0][:2]]

        def send_message(self, text, buttons=None):
            self.bot.write_message(self.id, text, buttons)

        def save(self):
            self.db.edit_player(self.player_id, self.current_admin, self.status)

    def __init__(self, mess, db, bots):
        player_id = mess["platform"] + mess["id"]
        self.mess = mess
        self.player = self.Player(player_id, db, bots)
        status_to_function = {
            "new_player": self.new_player,
            "main_menu": self.main_menu,
            "creating_game": self.creating_game,
            "game_admin": self.game_admin,
            "joining_game": self.joining_game,
            "game_player": self.game_player
        }
        func = status_to_function[self.player.status]
        func()
        self.player.save()

    def new_player(self):
        self.player.status = "main_menu"
        self.player.send_message("Привет, друг!! С помощью этого бота ты сможешь поиграть с друзьями в коднэймс:))")

    def main_menu(self):
        if self.mess["text"].lower() == "создать игру":
            self.player.status = "creating_game"
            self.player.send_message("Инициализация комнаты...\nЗадай ключ своей комнате")
        elif self.mess["text"].lower() == "войти в игру":
            self.player.status = "joining_game"
            self.player.send_message("Напиши ключ комнаты, к которой хочешь присоединиться")
        elif self.mess["text"].lower() == "правила":
            self.player.send_message("тут будут правила codenames")
        else:
            self.player.send_message("Не понял")

    def creating_game(self):
        pass

    def game_admin(self):
        pass

    def joining_game(self):
        pass

    def game_player(self):
        pass


class ConsoleBot:
    def __init__(self, events):
        self.events = events

    def main_loop(self):
        while True:
            text = input()
            self.events.append({
                "text": text,
                "first": "Benjamin",
                "last": "Counter",
                "id": "2281337",
                "platform": "cn"
            })

    @staticmethod
    def write_message(player_id, text, buttons=None):
        print(f"CONSOLE BOT sending to {player_id}: {text} ({buttons})")


class MainLoop:
    def __init__(self):
        self.db = Database()
        self.events = []

        self.bots = {
            "vk": VkBot(self.events),
            "cn": ConsoleBot(self.events)
        }
        # starting bots
        for name, bot in self.bots.items():
            bot_thread = threading.Thread(target=bot.main_loop)
            bot_thread.start()

        while True:
            if len(self.events) == 0:
                time.sleep(0.1)
                continue
            mess = self.events[-1]
            self.events.pop()
            try:
                Request(mess, self.db, bots=self.bots)
            except Exception as ex:
                print(f"!!! ERROR WHILE PARSING MESSAGE: {ex}")
                self.bots[mess["platform"]].write_message(mess["id"], "Произошла ошибка, дико извиняюсь")


if __name__ == '__main__':
    MainLoop()
