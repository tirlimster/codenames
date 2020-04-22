from random import randint, shuffle, seed
from json import loads


class Game:
	def __init__(self, field=None, mask=None, words=None, key=None):
		self.field = [[2] * 5 for x in range(5)] if field is None else field
		self.mask = [[0] * 5 for x in range(5)] if mask is None else mask
		self.words = [["лол"] * 5 for x in range(5)] if words is None else words

		if key is not None:
			seed(key)
			gen = [x for x in range(25)]
			shuffle(gen)
			for i in range(9):
				self.field[gen[i] // 5][gen[i] % 5] = 0
			for i in range(9, 9 + 8):
				self.field[gen[i] // 5][gen[i] % 5] = 1
			self.field[gen[17] // 5][gen[17] % 5] = 3

	def open(self, x, y):
		self.mask[y][x] = 1

	def showUser(self):
		return [[self.field[y][x] if self.mask[y][x] else 4 for x in range(5)] for y in range(5)]

	def showCaptain(self):
		return [[(self.mask[y][x], self.field[y][x]) for x in range(5)] for y in range(5)]
