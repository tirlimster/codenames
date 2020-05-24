import json
import sqlite3


class Commands:
    def __init__(self):
        with open("commands.json", "r", encoding="UTF-8") as file:
            self.values = json.loads(file.read())

    def __getitem__(self, item):
        return self.values[item]


class Database:
    DATABASE_NAME = "games_and_players.db"

    def __init__(self):
        self.connection = sqlite3.connect(self.DATABASE_NAME)
        self.cursor = self.connection.cursor()

    def restart(self):
        with self.connection:
            self.cursor.execute("""DROP TABLE IF EXISTS players""")
            self.cursor.execute("""DROP TABLE IF EXISTS games""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS players(
                player_id TEXT UNIQUE NOT NULL, 
                name TEXT,
                current_game TEXT, 
                status TEXT NOT NULL, 
                game_status INT
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS games(
                game_key TEXT UNIQUE, 
                players TEXT,
                field TEXT
            )""")

    def get_player(self, player_id):
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM players WHERE player_id = '{player_id}'""")
            return self.cursor.fetchone()

    def insert_player(self, player_id, name):
        if self.get_player(player_id):
            print("!!! inserting player twice")
            raise RuntimeError
        with self.connection:
            self.cursor.execute(f"""INSERT INTO players (player_id, status, game_status, name) 
                                    VALUES ('{player_id}', 'new_player', 0, '{name}')""")
        return self.get_player(player_id)

    def update_player(self, player):
        current_game = f"NULL" if player.current_game is None else f"'{player.current_game}'"
        with self.connection:
            self.cursor.execute(f"""
                UPDATE players SET current_game = {current_game}, status = '{player.status}',
                game_status = {player.game_status} WHERE player_id = '{player.player_id}'
            """)

    def get_game(self, game_key):
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM games WHERE game_key = '{game_key}'""")
            game = self.cursor.fetchone()
            if game is None:
                return None
            return game[1], json.loads(game[2]), json.loads(game[3])

    def create_game(self, game_key, creator):
        print(f"creating game with game_key={game_key}")
        with self.connection:
            players = json.dumps([[creator, 0]])
            new_field = json.dumps([[0, 0, 'а'] * 5 for _ in range(5)])
            self.cursor.execute(f"""
                INSERT INTO games (game_key, players, field) 
                VALUES ('{game_key}', '{players}', '{new_field}')
            """)
        return self.get_game(game_key)

    def save_game(self, game):
        field = json.dumps(game.board.field)
        players = json.dumps(game.game_players)
        with self.connection:
            self.cursor.execute(f"""
                UPDATE games SET field = '{field}', players = '{players}', WHERE game_key = '{game.key}'
            """)

    def delete_game(self, game_key):
        print(f"deleting game with game_key = {game_key}")
        with self.connection:
            self.cursor.execute(f"""DELETE FROM games WHERE game_key = '{game_key}'""")


if __name__ == '__main__':
    database = Database()
    database.restart()
