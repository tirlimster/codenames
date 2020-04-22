from random import shuffle, seed
from words_base import getWords


class Game:
	def __init__(self, field=None, mask=None, words=None, key=None):
		self.field = [[2] * 5 for _ in range(5)] if field is None else field
		self.mask = [[0] * 5 for _ in range(5)] if mask is None else mask
		if words is None:
			self.words = getWords(25, key)
			self.words = [[self.words[y * 5 + x] for x in range(5)] for y in range(5)]
		else:
			self.words = words

		if key is not None:
			seed(key)
			gen = [x for x in range(25)]
			shuffle(gen)
			for i in range(9):
				self.field[gen[i] // 5][gen[i] % 5] = 0
			for i in range(9, 9 + 8):
				self.field[gen[i] // 5][gen[i] % 5] = 1
			self.field[gen[9 + 8] // 5][gen[9 + 8] % 5] = 3

	def open(self, word):
		x, y = -1, -1
		for x0 in range(5):
			for y0 in range(5):
				if self.words[y0][x0] == word:
					x, y = x0, y0
		if (x, y) == (-1, -1):
			print("No such word found")
			raise KeyError
		self.mask[y][x] = 1

	def showUser(self):
		return [[self.field[y][x] if self.mask[y][x] else 4 for x in range(5)] for y in range(5)]

	def showCaptain(self):
		return [[(self.mask[y][x], self.field[y][x]) for x in range(5)] for y in range(5)]
