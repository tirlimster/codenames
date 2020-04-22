from json import loads, dumps
from random import shuffle, seed


def removeRepetitions():
	with open("words.json", 'r', encoding="utf-8") as f:
		ws = loads(f.read().strip())
		ws = [x.lower() for x in ws]
	ws = list(set(ws))
	with open("words.json", 'w', encoding="utf-8") as f:
		f.write(dumps(ws))


def addList(list):
	list = list.strip().split('\n')
	with open("words.json", 'r', encoding="utf-8") as f:
		ws = loads(f.read().strip())
	with open("words.json", 'w', encoding="utf-8") as f:
		f.write(dumps(ws + list))
	removeRepetitions()


def getList():
	with open("words.json", 'r', encoding="utf-8") as f:
		ws = loads(f.read().strip())
	return ws


def getWords(n, key=1543):
	seed(key)
	with open("words.json", 'r', encoding="utf-8") as f:
		ws = loads(f.read().strip())
	shuffle(ws)
	return ws[:n]
