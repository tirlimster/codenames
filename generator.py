from random import shuffle, seed
from words_base import getWords


class ConsoleBot:
    def __init__(self, events):
        self.events = events

    def main_loop(self):
        while True:
            text = input().split()
            self.events.append({
                "text": " ".join(text[1:]),
                "first": text[0],
                "last": "Surname",
                "id": text[0],
                "platform": "cn"
            })

    @staticmethod
    def write_message(player_id, text, buttons=None):
        print(f"CONSOLE BOT sending to {player_id}: {text} ({buttons})")


class Board:
    """
    Class Board used to generate codenames field
    field - array filled with {cell_type, flag_is_opened, word}
    cell_type: 0 - neutral, 1 - blue, 2 - red, 3 - bomb
    """

    def __init__(self, field):
        self.field = field
        self.h, self.w = (len(self.field), len(self.field[0])) if field is not None else (0, 0)

    def restart(self, key=None, h=8, w=3, t1=9, t2=8):
        self.h, self.w = h, w
        words_list = getWords(w * h, key)
        self.field = [[[0, 0, words_list[x * w + y]] for y in range(w)] for x in range(h)]
        if key is not None:
            seed(key)
        cells = [(i // w, i % w) for i in range(w * h)]
        shuffle(cells)
        for i in range(t1):
            self.field[cells[i][0]][cells[i][1]][0] = 1
        for i in range(t1, t1 + t2):
            self.field[cells[i][0]][cells[i][1]][0] = 2
        self.field[cells[t1 + t2][0]][cells[t1 + t2][1]][0] = 3

    def find_coords(self, word):
        x, y = -1, -1
        for x0 in range(self.w):
            for y0 in range(self.h):
                if self.field[y0][x0][2].lower() in word:
                    x, y = x0, y0
        return x, y

    def find(self, word):
        x, y = self.find_coords(word)
        if (x, y) == (-1, -1):
            return 2
        return self.field[y][x][1]

    def open(self, word):
        x, y = self.find_coords(word)
        if (x, y) == (-1, -1):
            print("No such word found")
            raise KeyError
        self.field[y][x][1] = 1

    def showUser(self):
        return self.field

    def showCaptain(self):
        return [[[cell[0], 1, cell[2]] for cell in row] for row in self.field]


if __name__ == '__main__':
    board = Board(None, None, None)
    board.restart()
    print(board.showCaptain())
    print(board.showUser())
