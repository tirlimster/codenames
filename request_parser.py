import time
import random
import threading
# from vk_bot import VkBot
from tg_bot import TgBot
from generator import Board, ConsoleBot
from database import Database, Commands

COMMANDS = Commands()


class Players:
    class Player:
        def __init__(self, player_id, db, bots, name=None):
            self.db = db
            data = self.db.get_player(player_id)
            if data is None:
                data = self.db.insert_player(player_id, name)
            self.player_id, self.name, self.current_game, self.status = data
            self.game_status = 0

            self.bot = bots[data[0][:2]]
            self.out_message = ""
            self.board = []

        def __del__(self):
            if self.out_message:
                # todo make buttons
                self.bot.write_message(self.player_id[2:], self.out_message.strip(), self.buttons + self.board)
            self.db.edit_player(self.player_id, self.current_game, self.status)
            # print(f"Player {self.player_id} saved")

        def send_message(self, text):
            if text is not "":
                self.out_message += text + "\n\n"

    def __init__(self, db, bots, player_id, mess):
        self.db, self.bots = db, bots
        self.players_dict = {}
        self.sender = self.add_player(player_id, mess)

    def __getitem__(self, item):
        return self.players_dict[item]

    def add_player(self, player_id, mess=None):
        if player_id in self.players_dict:
            return
        name = None if mess is None else f"{mess['first']} {mess['second']}"
        self.players_dict[player_id] = self.Player(player_id, self.db, self.bots, name)
        return self.players_dict[player_id]


class Game:
    def __init__(self, db, players, game_key):
        self.db = db
        self.players = players
        data = self.db.get_game(game_key)
        if data is None:
            data = self.db.create_game(game_key)

        self.key, self.game_players = data[0], data[1]
        self.board = Board(data[2])

    def __del__(self):
        for player in self.players:
            if player.game_status in [1, 2]:
                player.send_message("", self.board.showUser())
            if player.game_status in [3, 4]:
                player.send_message("", self.board.showCaptain())
        self.db.save_game(self)

    def send_admin(self, text):
        self.players[self.game_players[0]].send_message(text)

    def start_game(self):
        if len(self.game_players) < 4:
            self.send_admin("Не хватает игроков, чтобы начать игру. Нужно хотя бы 4")
            return
        trans = [i for i in range(len(self.game_players))]
        random.shuffle(trans)
        self.players[self.game_players[trans[0]]].game_status = 3
        self.players[self.game_players[trans[1]]].game_status = 4

        t1, t2 = (len(self.players) - 1) // 2, (len(self.players) - 2) // 2
        if 2 + t1 + t2 != len(self.players):
            raise RuntimeError
        for i in range(2, 2 + t1):
            self.players[self.game_players[trans[i]]].game_status = 1
        for i in range(2 + t1, 2 + t1 + t2):
            self.players[self.game_players[trans[i]]].game_status = 2
        self.board.restart()

        blue, red = "Синие:\n", "Красные:\n"
        for p_id in self.game_players:
            name = self.players[p_id].name
            if self.players[p_id].game_status in [3, 4]:
                name += " - капитан"
            if self.players[p_id].game_status % 2:
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

    def add_sender(self):
        self.players.sender.current_game = self.key
        self.send_admin(f"{self.players.sender.name} присоединился к комнате")

    def delete_sender(self):
        self.players.sender.status = "main_menu"
        self.players.sender.send_message(f"Ты вышел из комнаты")
        self.send_admin(f"{self.players.sender.name} покинул комнату")
        self.game_players = [p for p in self.game_players if self.game_players]

    def open_word(self, word):
        if self.players.sender.game_status == 0:
            self.players.sender.send_message("Ты не в игре, подожди, пока админ перезапустит игру")
        if self.players.sender.game_status in [3, 4]:
            self.players.sender.send_message("Ты капитан, куда ты тыкаешь???")
        else:
            self.board.open(word)
            for p_id in self.game_players:
                if self.players.sender.player_id == p_id:
                    self.players[p_id].send_message(f"Ты открыл слово {word}")
                else:
                    self.players[p_id].send_message(f"{self.players.sender.name} открывает слово {word}")

    def delete_game(self):
        for p_id in self.game_players:
            self.players[p_id].status = "main_menu"
            self.players[p_id].game_status = 0
            self.players[p_id].send_message(f"Комната удалена")
        self.db.delete_game(self.players.sender.current_game)


class Request:
    def __init__(self, mess, db, bots):
        player_id = mess["platform"] + mess["id"]
        self.db = db
        self.bots = bots
        self.lwr = mess["text"].lower()
        self.players = Players(player_id, self.db, self.bots, mess)

        getattr(self, self.players.sender.status)()

    def new_player(self):
        self.players.sender.send_message(
            "Привет, друг!! С помощью этого бота ты сможешь поиграть с друзьями в коднэймс:))"
        )

    def unknown(self):
        self.players.sender.send_message("Не понял")

    def menu(self):
        self.players.sender.status = "main_menu"
        self.players.sender.send_message("Ты в главном меню")

        # todo commands parser
        self.players.sender.status = "creating_game"
        self.players.sender.send_message("Инициализация комнаты...\nЗадай ключ своей комнате")

    def show_rules(self):
        self.players.sender.send_message("тут будут правила codenames")

    def joining(self):
        self.players.sender.status = "joining_game"
        self.players.sender.send_message("Напиши ключ комнаты, к которой хочешь присоединиться")

    def to_delete_room(self):
        game = Game(self.db, self.players, self.players.sender.current_game)
        game.delete_game()

    def to_leave_room(self):
        game = Game(self.db, self.players, self.players.sender.current_game)
        game.delete_sender()

    def creating(self):
        if self.db.get_game(game_key=self.lwr) is None:
            self.players.sender.status = "game_admin"
            Game(self.db, self.players, self.lwr)
            self.players.sender.send_message(f"Игра с ключом {self.lwr} создана")
        else:
            self.players.sender.send_message(f"Игра с таким ключом уже есть")

    def to_game_player(self):
        if self.db.get_game(game_key=self.lwr) is not None:
            self.players.sender.status = "game_player"
            game = Game(self.db, self.players, self.lwr)
            game.add_sender()
            self.players.sender.send_message(f"Вы подключены к игре с ключом {self.lwr}")
        else:
            self.players.sender.send_message(f"Игры с таким ключом нет")

    def to_game_restart(self):
        game = Game(self.db, self.players, self.players.sender.current_game)
        game.start_game()

    def parse_game(self):
        game = Game(self.db, self.players, self.players.sender.current_game)
        if self.players.sender.game_status in [3, 4]:
            self.players.sender.send_message(f"Ты капитан, куда ты тыкаешь???")
            return
        res = game.find_word(self.lwr)
        if res == 1:
            self.players.sender.send_message(f"Такого слова нет")
        if res == 2:
            self.players.sender.send_message(f"Это слово уже открыто")
        if res == 3:
            game.open_word(self.lwr)


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
