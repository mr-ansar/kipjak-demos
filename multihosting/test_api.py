# test_api.py
import kipjak as kj

class Xy(object):
	def __init__(self, x: int=1, y: int=1):
		self.x = x
		self.y = y

kj.bind(Xy)

class Customer(object):
	def __init__(self, name: str=None, age: int=None):
		self.name = name
		self.age = age

kj.bind(Customer)

table_type = kj.def_type(list[list[float]])
