import time
import random
import threading
from vk_bot import VkBot
from tg_bot import TgBot
from generator import Board
from database import Database


class Player:
    def __init__(self, player_id, db, bots, name=None):
        self.db = db
        data = self.db.get_player(player_id)
        if data is None:
            data = self.db.insert_player(player_id, name)
        self.player_id, self.name, self.current_game, self.status = data

        self.platform_id = data[0][2:]
        self.bot = bots[data[0][:2]]

        self.out_mess = ""
        self.out_buttons = []

    def __del__(self):
        if self.out_mess:
            self.bot.write_message(self.platform_id, self.out_mess.strip(), self.out_buttons)
        print(f"Player {self.player_id} saved")
        self.save()

    def send_message(self, text, buttons=None):
        if text:
            self.out_mess += text + "\n\n"
        if buttons is not None:
            self.out_buttons.append(buttons)

    def save(self):
        self.db.edit_player(self.player_id, self.current_game, self.status)

    def start_game(self, game_key):
        self.db.start_game(self.player_id, game_key)


class Game:
    def __init__(self, db, bots, admin_id=None, game_key=None):
        self.db = db
        self.bots = bots
        data = self.db.get_game(admin_id=admin_id, game_key=game_key)
        if data is None:
            data = self.db.create_game(admin_id=admin_id, game_key=game_key)

        self.admin, self.key = Player(data[0], self.db, self.bots), data[2]
        self.players = [[Player(p[0], self.db, self.bots), p[1]] for p in data[1]]
        self.board = Board(data[3], data[4], data[5])

    def __del__(self):
        self.db.save_game(self)

    def send_message(self, text, buttons=None):
        for player in self.players:
            player[0].send_message(text, buttons)

    def start_game(self):
        if len(self.players) < 4:
            self.admin.send_message("Не хватает игроков, чтобы начать игру. Нужно хотя бы 4")
        random.shuffle(self.players)
        self.players[0][1], self.players[1][1] = 3, 4

        first_cnt, second_cnt = (len(self.players) - 1) // 2, (len(self.players) - 2) // 2
        if 2 + first_cnt + second_cnt != len(self.players):
            raise RuntimeError
        for i in range(2, 2 + first_cnt):
            self.players[i][1] = 1
        for i in range(2 + first_cnt, 2 + first_cnt + second_cnt):
            self.players[i][1] = 2
        self.board.restart()

        blue, red = "", ""
        for player in self.players:
            name = player[0].name
            if player[1] > 2:
                name += " - капитан"
            if player[1] % 2:
                blue += name + "\n"
            else:
                red += name + "\n"

        for player in self.players:
            player[0].send_message("Поделились на команды...\n" + blue + red)
            if player[1] > 2:
                player[0].send_message("Ты капитан. Вот такое поле сгенерировалось", self.board.showCaptain())
            else:
                player[0].send_message("Вот такие вот слова", self.board.showUser())

    def find_word(self, word):
        return self.board.find(word)

    def add_player(self, player):
        player.current_game = self.key
        self.admin.send_message(f"{player.name} присоединился к комнате")
        self.players.append(player)

    def delete_player(self, player):
        index = -1
        for i in range(len(self.players)):
            if self.players[i] == player:
                index = i
        if index == -1:
            print("** !!! delete_player: no player found")
            raise RuntimeError
        self.players.pop(index)

    def open_word(self, player, word):
        role = -1
        for p in self.players:
            if p[0] == player:
                role = p[1]
        if role <= 0:
            print(f"**(open word): Player has role = {role}")
            raise RuntimeError
        if role > 2:
            player.send_message("Ты капитан, куда ты тыкаешь???")
        else:
            self.board.open(word)
            for p in self.players:
                if p[1] > 2:
                    p[0].send_message(f"{player.name} открывает слово {word}", self.board.showCaptain())
                else:
                    p[0].send_message(f"{player.name} открывает слово {word}", self.board.showUser())

    def delete_game(self):
        for player in self.players:
            player[0].send_message(f"Комната удалена")
            player[0].status = "main_menu"
        self.db.delete_game(self.admin)


class Request:
    def __init__(self, mess, db, bots):
        player_id = mess["platform"] + mess["id"]
        self.db = db
        self.bots = bots
        self.mess = mess
        self.lwr = mess["text"].lower()
        self.player = Player(player_id, self.db, self.bots, f"{mess['first']} {mess['last']}")

        commands = {
            "to_unknown": [
                lambda x: True,
                self.to_unknown,
                None
            ],
            "to_new_user": [
                lambda x: True,
                self.to_main_menu,
                None
            ],
            "to_main_menu": [
                lambda x: "меню" in x,
                self.to_main_menu,
                "Назад в меню"
            ],
            "to_creating_game": [
                lambda x: x in ["создать игру", "новая игра"],
                self.to_creating_game,
                "Создать игру"
            ],
            "to_joining_game": [
                lambda x: x in ["войти в игру", "присоединится"],
                self.to_joining_game,
                "Войти в игру"
            ],
            "to_game_admin": [
                lambda x: len(x) < 12,
                self.to_game_admin,
                None
            ],
            "to_game_player": [
                lambda x: len(x) < 12,
                self.to_game_player,
                None
            ],
            "to_rules": [
                lambda x: x == "правила",
                self.to_rules,
                "Правила"
            ],
            "parse_game": [
                lambda x: True,
                self.parse_game,
                None
            ],
            "to_delete_room": [
                lambda x: x == "удалить комнату",
                self.to_delete_room,
                "Удалить комнату"
            ],
            "to_leave_room": [
                lambda x: x == "выйти из комнаты",
                self.to_leave_room,
                "Выйти из комнаты"
            ]
        }

        status_commands = {
            "new_player": [
                commands["to_new_user"]
            ],
            "main_menu": [
                commands["to_creating_game"],
                commands["to_joining_game"],
                commands["to_rules"],
                commands["to_unknown"]
            ],
            "creating_game": [
                commands["to_main_menu"],
                commands["to_game_admin"],
                commands["to_unknown"]
            ],
            "joining_game": [
                commands["to_main_menu"],
                commands["to_game_player"],
                commands["to_unknown"]
            ],
            "game_admin": [
                commands["to_delete_room"],
                commands["parse_game"],
            ],
            "game_player": [
                commands["to_leave_room"],
                commands["parse_game"]
            ]
        }

        for cmp, action, button in status_commands[self.player.status]:
            if cmp(self.lwr):
                action()
                break
        for cmp, action, button in status_commands[self.player.status]:
            if button is not None:
                self.player.send_message("", [button])

    def to_unknown(self):
        self.player.send_message("Не понял")

    def to_main_menu(self):
        self.player.status = "main_menu"
        if self.player.status:
            self.player.send_message("Ты в главном меню")
        else:
            self.player.send_message("Привет, друг!! С помощью этого бота ты сможешь поиграть с друзьями в коднэймс:))")

    def to_rules(self):
        self.player.send_message("тут будут правила codenames")

    def to_creating_game(self):
        self.player.status = "creating_game"
        self.player.send_message("Инициализация комнаты...\nЗадай ключ своей комнате")

    def to_joining_game(self):
        self.player.status = "joining_game"
        self.player.send_message("Напиши ключ комнаты, к которой хочешь присоединиться")

    def to_delete_room(self):
        game = Game(self.db, self.bots, admin_id=self.player.player_id)
        game.delete_game()

    def to_leave_room(self):
        game = Game(self.db, self.bots, game_key=self.player.current_game)
        game.delete_player(self.player.platform_id)

    def to_game_admin(self):
        if self.db.get_game(game_key=self.lwr) is None:
            self.player.status = "game_admin"
            Game(self.db, self.bots, admin_id=self.player.player_id, game_key=self.lwr)
            self.player.send_message(f"Игра с ключом {self.lwr} создана")
        else:
            self.player.send_message(f"Игра с таким ключом уже есть")

    def to_game_player(self):
        if self.db.get_game(game_key=self.lwr) is not None:
            self.player.status = "game_player"
            game = Game(self.db, self.bots, game_key=self.lwr)
            game.add_player(self.player)
            self.player.send_message(f"Вы подключены к игре с ключом {self.lwr}")
        else:
            self.player.send_message(f"Игры с таким ключом нет")

    def parse_game(self):
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
            # "tg": TgBot(self.events),
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
            # try:
            Request(mess, self.db, bots=self.bots)
            # except Exception as ex:
            #     print(f"!!! ERROR WHILE PARSING MESSAGE: {ex.args}")
            #     self.bots[mess["platform"]].write_message(mess["id"], "Произошла ошибка, дико извиняюсь")


if __name__ == '__main__':
    MainLoop()
