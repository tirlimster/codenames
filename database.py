import json
import sqlite3
from generator import Game


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
                player_id TEXT UNIQUE, 
                player_name TEXT UNIQUE, 
                current_admin TEXT
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS games(
                admin_id TEXT UNIQUE REFERENCES players(player_id),
                field TEXT, 
                mask TEXT, 
                words TEXT,
                game_key TEXT UNIQUE
            )""")

    def get_player(self, player_id):
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM players WHERE player_id = '{player_id}'""")
            return self.cursor.fetchall()

    def insert_player(self, player_id):
        if self.get_player(player_id):
            return
        with self.connection:
            self.cursor.execute(f"""INSERT INTO players (player_id) VALUES ('{player_id}')""")

    def edit_players_game(self, player_id, admin_id):
        current_admin = f"NULL" if admin_id is None else f"'{admin_id}'"
        with self.connection:
            self.cursor.execute(f"""
                UPDATE players SET current_admin = {current_admin} WHERE player_id = '{player_id}'
            """)

    def start_game(self, admin_id, game_key):
        with self.connection:
            game = Game(game_key)
            field_string = json.dumps(game.field)
            mask_string = json.dumps(game.mask)
            words_string = json.dumps(game.mask)

            self.cursor.execute(f"""
                INSERT INTO games (admin_id, field, mask, words, game_key) 
                VALUES ('{admin_id}', '{field_string}', '{mask_string}', '{words_string}', '{game_key}')
            """)
        self.edit_players_game(admin_id, admin_id)

    def delete_game(self, admin_id):
        with self.connection:
            self.cursor.execute(f"""DELETE FROM games WHERE admin_id = '{admin_id}'""")

    @staticmethod
    def convert_game(fetched):
        field = json.loads(fetched[1])
        mask = json.loads(fetched[2])
        words = json.loads(fetched[3])
        return Game(field, mask, words)

    def get_game_by_admin(self, admin_id):
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM games WHERE admin_id = '{admin_id}'""")
            return self.convert_game(self.cursor.fetchone())

    def get_game_by_key(self, game_key):
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM games WHERE game_key = '{game_key}'""")
            return self.convert_game(self.cursor.fetchone())

    def edit_game(self, admin_id, game):
        with self.connection:
            field_string = json.dumps(game.field)
            mask_string = json.dumps(game.mask)
            words_string = json.dumps(game.mask)

            self.cursor.execute(f"""
                UPDATE games SET field = '{field_string}', mask = '{mask_string}', words = '{words_string}' 
                WHERE admin_id = '{admin_id}'
            """)


if __name__ == '__main__':
    database = Database()
    database.restart()
