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
        self.game_status = 0

        self.bot = bots[data[0][:2]]
        self.out_message, self.out_buttons = "", []

    def __del__(self):
        if self.out_message:
            self.bot.write_message(self.player_id[2:], self.out_message.strip(), self.out_buttons)
        self.db.edit_player(self.player_id, self.current_game, self.status)
        # print(f"Player {self.player_id} saved")

    def send_message(self, text, buttons=None):
        if text is not "":
            self.out_message += text + "\n\n"
        if buttons is not None:
            self.out_buttons += buttons


class Game:
    def __init__(self, db, bots, players, admin_id=None, game_key=None):
        self.db = db
        self.bots = bots
        self.players = players
        data = self.db.get_game(admin_id=admin_id, game_key=game_key)
        if data is None:
            data = self.db.create_game(admin_id=admin_id, game_key=game_key)
        self.admin, self.key = -1, data[2]

        ind_by_id = dict()
        for i in range(len(self.players)):
            ind_by_id[self.players[i].player_id] = i
        for p in data[1]:
            if p[0] not in ind_by_id:
                ind_by_id[p[0]] = len(self.players)
                self.players.append(Player(p[0], self.db, self.bots))
            self.players[ind_by_id[p[0]]].game_status = p[1]

        for i in range(len(self.players)):
            if self.players[i].player_id == data[0]:
                self.admin = i
        self.deleted = -1
        self.board = Board(data[3], data[4], data[5])

    def __del__(self):
        for player in self.players:
            if player.game_status in [3, 4]:
                player.send_message("", self.board.showCaptain())
            if player.game_status in [1, 2]:
                player.send_message("", self.board.showUser())
        self.db.save_game(self)

    def send_admin(self, text, buttons=None):
        self.players[self.admin].send_message(text, buttons)

    def start_game(self):
        if len(self.players) < 4:
            self.send_admin("Не хватает игроков, чтобы начать игру. Нужно хотя бы 4")
            return
        random.shuffle(self.players)
        self.players[0].game_status, self.players[1].game_status = 3, 4

        t1, t2 = (len(self.players) - 1) // 2, (len(self.players) - 2) // 2
        if 2 + t1 + t2 != len(self.players):
            raise RuntimeError
        for i in range(2, 2 + t1):
            self.players[i].game_status = 1
        for i in range(2 + t1, 2 + t1 + t2):
            self.players[i].game_status = 2
        self.board.restart()

        blue, red = "Синие:\n", "Красные:\n"
        for player in self.players:
            name = player.name
            if player.game_status in [3, 4]:
                name += " - капитан"
            if player.game_status % 2:
                blue += name + "\n"
            else:
                red += name + "\n"

        for player in self.players:
            player.send_message("Поделились на команды...\n\n" + blue + "\n" + red)
            if player.status in [3, 4]:
                player.send_message("Ты капитан. Вот такое поле сгенерировалось")
            else:
                player.send_message("Вот такие вот слова")

    def find_word(self, word):
        return self.board.find(word)

    def add_player(self, ind=0):
        self.players[ind].current_game = self.key
        self.send_admin(f"{self.players[ind].name} присоединился к комнате")

    def delete_player(self, ind=0):
        self.players[ind].status = "main_menu"
        self.players[ind].send_message(f"Ты вышел из комнаты")
        self.send_admin(f"{self.players[ind].name} покинул комнату")
        self.deleted = ind

    def open_word(self, word):
        if self.players[0].game_status > 2:
            self.players[0].send_message("Ты капитан, куда ты тыкаешь???")
        else:
            self.board.open(word)
            for p in self.players:
                if p.game_status in [3, 4]:
                    p.send_message(f"{self.players[0].name} открывает слово {word}")
                elif p.game_status in [1, 2]:
                    p.send_message(f"{self.players[0].name} открывает слово {word}")

    def delete_game(self, menu_buttons):
        for player in self.players:
            player.status = "main_menu"
            player.game_status = 0
            player.send_message(f"Комната удалена")
            if player != self.players[0]:
                player.send_message("", menu_buttons)
        self.db.delete_game(self.players[self.admin].player_id)


class Request:
    def __init__(self, mess, db, bots):
        player_id = mess["platform"] + mess["id"]
        self.db = db
        self.bots = bots
        self.mess = mess
        self.lwr = mess["text"].lower()
        self.players = [Player(player_id, self.db, self.bots, f"{mess['first']} {mess['last']}")]

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
            ],
            "to_game_restart": [
                lambda x: x == "новая игра",
                self.to_game_restart,
                "Новая игра"
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
                commands["to_game_restart"],
                commands["parse_game"],
            ],
            "game_player": [
                commands["to_leave_room"],
                commands["parse_game"]
            ]
        }
        self.menu_buttons = []
        for com in status_commands["main_menu"]:
            if com[2] is not None:
                self.menu_buttons.append([com[2]])

        for cmp, action, button in status_commands[self.players[0].status]:
            if cmp(self.lwr):
                action()
                break
        for cmp, action, button in status_commands[self.players[0].status]:
            if button is not None:
                self.players[0].send_message("", [[button]])

    def to_unknown(self):
        self.players[0].send_message("Не понял")

    def to_main_menu(self):
        self.players[0].status = "main_menu"
        if self.players[0].status:
            self.players[0].send_message("Ты в главном меню")
        else:
            self.players[0].send_message(
                "Привет, друг!! С помощью этого бота ты сможешь поиграть с друзьями в коднэймс:))"
            )

    def to_rules(self):
        self.players[0].send_message("тут будут правила codenames")

    def to_creating_game(self):
        self.players[0].status = "creating_game"
        self.players[0].send_message("Инициализация комнаты...\nЗадай ключ своей комнате")

    def to_joining_game(self):
        self.players[0].status = "joining_game"
        self.players[0].send_message("Напиши ключ комнаты, к которой хочешь присоединиться")

    def to_delete_room(self):
        game = Game(self.db, self.bots, self.players, admin_id=self.players[0].player_id)
        game.delete_game(self.menu_buttons)

    def to_leave_room(self):
        game = Game(self.db, self.bots, self.players, game_key=self.players[0].current_game)
        game.delete_player()

    def to_game_admin(self):
        if self.db.get_game(game_key=self.lwr) is None:
            self.players[0].status = "game_admin"
            Game(self.db, self.bots, self.players, admin_id=self.players[0].player_id, game_key=self.lwr)
            self.players[0].send_message(f"Игра с ключом {self.lwr} создана")
        else:
            self.players[0].send_message(f"Игра с таким ключом уже есть")

    def to_game_player(self):
        if self.db.get_game(game_key=self.lwr) is not None:
            self.players[0].status = "game_player"
            game = Game(self.db, self.bots, self.players, game_key=self.lwr)
            game.add_player()
            self.players[0].send_message(f"Вы подключены к игре с ключом {self.lwr}")
        else:
            self.players[0].send_message(f"Игры с таким ключом нет")

    def to_game_restart(self):
        game = Game(self.db, self.bots, self.players, game_key=self.players[0].current_game)
        game.start_game()

    def parse_game(self):
        game = Game(self.db, self.bots, self.players, game_key=self.players[0].current_game)
        if self.players[0].game_status in [3, 4]:
            self.players[0].send_message(f"Ты капитан, куда ты тыкаешь???")
            return
        res = game.find_word(self.lwr)
        if res == 1:
            self.players[0].send_message(f"Такого слова нет")
        if res == 2:
            self.players[0].send_message(f"Это слово уже открыто")
        if res == 3:
            game.open_word(self.lwr)


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
            # "vk": VkBot(self.events),
            "tg": TgBot(self.events),
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
                print(f"!!! ERROR WHILE PARSING MESSAGE: {ex.args}")
                self.bots[mess["platform"]].write_message(mess["id"], "Произошла ошибка, дико извиняюсь")


if __name__ == '__main__':
    MainLoop()
