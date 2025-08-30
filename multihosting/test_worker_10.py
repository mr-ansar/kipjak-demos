# test_worker_10.py
import uuid
import kipjak as kj
from test_api import Xy, table_type
from test_function_10 import texture

def worker(self):
	tag = uuid.uuid4()
	kj.publish(self, f'test-multihosting:worker-10:{tag}', scope=kj.ScopeOfDirectory.LAN)
	m = self.input()
	if not isinstance(m, kj.Published):
		return m

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

kj.bind(worker, entry_point=[Xy,])

if __name__ == '__main__':
	kj.create(worker)
