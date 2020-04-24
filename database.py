import json
import sqlite3


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
                status TEXT NOT NULL
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS games(
                admin_id TEXT UNIQUE REFERENCES players(player_id),
                players TEXT,
                game_key TEXT UNIQUE, 
                field TEXT, 
                mask TEXT, 
                words TEXT
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
            self.cursor.execute(f"""INSERT INTO players (player_id, status, name) 
                                    VALUES ('{player_id}', 'new_player', '{name}')""")
        return self.get_player(player_id)

    def edit_player(self, player_id, game_id, status):
        current_game = f"NULL" if game_id is None else f"'{game_id}'"
        with self.connection:
            self.cursor.execute(f"""
                UPDATE players SET current_game = {current_game}, status = '{status}'
                WHERE player_id = '{player_id}'
            """)

    def get_game(self, admin_id=None, game_key=None):
        id_cond = "TRUE" if admin_id is None else f"admin_id = '{admin_id}'"
        key_cond = "TRUE" if game_key is None else f"game_key = '{game_key}'"
        with self.connection:
            self.cursor.execute(f"""SELECT * FROM games WHERE {id_cond} AND {key_cond}""")
            game = self.cursor.fetchone()
            if game is None:
                return None
            return game[0], json.loads(game[1]), game[2], json.loads(game[3]), json.loads(game[4]), json.loads(game[5])

    def create_game(self, admin_id, game_key):
        with self.connection:
            players = json.dumps([[admin_id, 0]])
            new_field = json.dumps([[0] * 5 for _ in range(5)])
            new_mask = json.dumps([[0] * 5 for _ in range(5)])
            new_words = json.dumps([["a"] * 5 for _ in range(5)])
            self.cursor.execute(f"""
                INSERT INTO games (admin_id, game_key, players, field, mask, words) 
                VALUES ('{admin_id}', '{game_key}', '{players}', '{new_field}', '{new_mask}', '{new_words}')
            """)
        return self.get_game(admin_id, game_key)

    def save_game(self, game):
        field, mask, words, players = map(
            json.dumps, [game.board.field, game.board.mask, game.board.words, game.players]
        )
        with self.connection:
            self.cursor.execute(f"""
                UPDATE games SET field = '{field}', mask = '{mask}', words = '{words}', players = '{players}',
                admin_id = '{game.admin}' WHERE game_key = '{game.key}'
           """)

    def delete_game(self, admin_id):
        with self.connection:
            self.cursor.execute(f"""DELETE FROM games WHERE admin_id = '{admin_id}'""")


if __name__ == '__main__':
    database = Database()
    database.restart()
