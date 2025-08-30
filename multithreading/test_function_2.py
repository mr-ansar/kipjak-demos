# test_function_2.py
import random
import kipjak as kj

random.seed()

def texture(self, x: int=8, y: int=8) -> list[list[float]]:
	table = []
	for r in range(y):
		row = [None] * x
		table.append(row)
		for c in range(x):
			row[c] = random.random()

	return table

kj.bind(texture)
