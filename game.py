from random import randint, shuffle, seed

class Game:
	def __init__(self, key):
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
		mask[y][x] = 1
		return self.field[y][x]

	def showUser(self):
		return [[self.field[y][x] if self.mask[y][x] else 4 for x in range(5)] for y in range(5)]

	def showCaptain(self):
		return [[(self.mask[y][x], self.field[y][x]) for x in range(5)] for y in range(5)]
