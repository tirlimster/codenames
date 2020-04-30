from random import shuffle, seed
from words_base import getWords


class Board:
    """
    Class Board used to generate codenames field
    cell_type: 0 - not_opened, 1 - neutral, 2 - blue, red - 3, 4 - bomb
    """

    def __init__(self, field, mask, words):
        self.field, self.mask, self.words = field, mask, words
        self.h, self.w = (len(self.field), len(self.field[0])) if field is not None else (0, 0)

    def restart(self, key=None, h=4, w=5, t1=9, t2=8):
        self.h, self.w = h, w
        self.field = [[1] * w for _ in range(h)]
        self.mask = [[0] * w for _ in range(h)]
        words_list = getWords(w * h, key)
        self.words = [[words_list[y * w + x] for x in range(w)] for y in range(h)]
        if key is not None:
            seed(key)
        gen = [x for x in range(w * h)]
        shuffle(gen)
        for i in range(t1):
            self.field[gen[i] // w][gen[i] % w] = 2
        for i in range(t1, t1 + t2):
            self.field[gen[i] // w][gen[i] % w] = 3
        self.field[gen[t1 + t2] // 5][gen[t1 + t2] % 5] = 4

    def find(self, word):
        x, y = -1, -1
        for x0 in range(self.w):
            for y0 in range(self.h):
                if word in self.words[y0][x0]:
                    x, y = x0, y0
        if (x, y) == (-1, -1):
            return 1
        if self.mask[y][x]:
            return 2
        return 0

    def open(self, word):
        x, y = -1, -1
        for x0 in range(self.w):
            for y0 in range(self.h):
                if word in self.words[y0][x0]:
                    x, y = x0, y0
        if (x, y) == (-1, -1):
            print("No such word found")
            raise KeyError
        self.mask[y][x] = 1
        return self.field[y][x]

    def showUser(self):
        return [[(self.words[y][x], self.field[y][x] if self.mask[y][x] else 0, 0)
                 for x in range(self.w)] for y in range(self.h)]

    def showCaptain(self):
        return [[(self.words[y][x], self.field[y][x], self.mask[y][x])
                 for x in range(self.w)] for y in range(self.h)]


if __name__ == '__main__':
    board = Board(None, None, None)
    board.restart()
    print(board.showCaptain())
    print(board.showUser())
