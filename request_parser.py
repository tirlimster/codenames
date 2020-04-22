import time
import threading
from database import Database
from vk_bot import VkBot


class Request:
    class Player:
        def __init__(self, data, bots):
            self.player_id = data[0]
            self.current_admin = data[2]
            self.id = data[0][2:]
            self.bot = bots[data[0][:2]]

        def send_message(self, text, buttons=None):
            self.bot.write_message(self.id, text, buttons)

    def __init__(self, mess, db, bots):
        player_id = mess["platform"] + mess["id"]
        data = self.db.get_player(player_id)
        if data is None:
            self.db.insert_player(player_id)
            self.new_player(mess)
            return

        self.db = db
        self.player = self.Player(data, bots)
        if self.player.current_admin is None:
            self.in_game_player(mess)
        else:
            self.out_game_player(mess)

    def new_player(self, mess):
        print("privet chel!!!")
        pass

    def in_game_player(self, mess):
        pass

    def out_game_player(self, mess):
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
                "platform": "is_on_the_right"
            })

    @staticmethod
    def write_message(player_id, text, buttons=None):
        print(f"to {player_id}: {text} ({buttons})")


class MainLoop:
    def __init__(self):
        self.db = Database()
        self.events = []

        self.bots = {
            "vk": VkBot(self.events),
            "is": ConsoleBot(self.events)
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
                # TODO error message to user


if __name__ == '__main__':
    MainLoop()
