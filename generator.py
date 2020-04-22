from random import randint, shuffle, seed

class Game:
	def init(self, field, mask, words):
		self.field = field
		self.mask = mask
		self.words = words

	def __init__(self, key, mask=None, words=None):
		if (words != None):
			self.init(key, mask, words)
			return
		seed(key)
		self.field = [[2] * 5 for x in range(5)]
		gen = [x for x in range(25)]
		shuffle(gen)
		for i in range(9):
			self.field[gen[i] // 5][gen[i] % 5] = 0
		for i in range(9, 17):
			self.field[gen[i] // 5][gen[i] % 5] = 1
		self.field[gen[17] // 5][gen[17] % 5] = 3
		self.mask = [[0] * 5 for x in range(5)]

	def open(self, x, y):
		self.mask[y][x] = 1
		return self.field[y][x]

	def showUser(self):
		return [[self.field[y][x] if self.mask[y][x] else 4 for x in range(5)] for y in range(5)]

	def showCaptain(self):
		return [[(self.mask[y][x], self.field[y][x]) for x in range(5)] for y in range(5)]