# test_worker_4.py
import kipjak as kj
from test_api import Xy, table_type
from test_function_4 import texture

def worker(self):
	while True:
		m = self.input()
		if isinstance(m, Xy):
			pass
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.Stop):
			return kj.Aborted()
		else:
			continue

		table = texture(x=m.x, y=m.y)
		self.send(kj.cast_to(table, table_type), self.return_address)

kj.bind(worker)
