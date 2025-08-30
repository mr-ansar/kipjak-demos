# test_server_5.py
import kipjak as kj
from test_api import Xy, table_type
from test_function_5 import texture

DEFAULT_ADDRESS = kj.HostPort('127.0.0.1', 5050)
SERVER_API = [Xy,]

def server(self, server_address: kj.HostPort=None):
	server_address = server_address or DEFAULT_ADDRESS

	kj.listen(self, server_address, http_server=SERVER_API)
	m = self.input()
	if not isinstance(m, kj.Listening):
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

		client_address = self.return_address
		self.create(kj.ProcessObject, texture, x=m.x, y=m.y)
		m = self.input()
		response = m.message

		self.send(response, client_address)

kj.bind(server)

if __name__ == '__main__':
	kj.create(server)
