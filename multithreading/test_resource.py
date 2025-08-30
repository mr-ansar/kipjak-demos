# test_resource.py
import kipjak as kj

class Customer(object):
	def __init__(self, name: str=None, age: int=None):
		self.name = name
		self.age = age

kj.bind(Customer)
