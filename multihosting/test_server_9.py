# test_server_9.py
import kipjak as kj
from test_api import Xy

DEFAULT_ADDRESS = kj.HostPort('127.0.0.1', 5050)
SERVER_API = [Xy,]

def server(self, server_address: kj.HostPort=None):
	server_address = server_address or DEFAULT_ADDRESS

	kj.listen(self, server_address, http_server=SERVER_API)
	m = self.input()
	if not isinstance(m, kj.Listening):
		return m

	kj.subscribe(self, 'test-multihosting:worker-9')
	m = self.input()
	if not isinstance(m, kj.Subscribed):
		return m

	worker_spool = self.create(kj.ObjectSpool, None)

	while True:
		m = self.input()
		if isinstance(m, Xy):
			pass
		elif isinstance(m, kj.Returned):
			d = self.debrief()
			if isinstance(d, kj.OnReturned):
				d(self, m)
			continue
		elif isinstance(m, kj.Available):
			self.send(kj.JoinSpool(m.publisher_address), worker_spool)
			continue
		elif isinstance(m, kj.Dropped):
			self.send(kj.LeaveSpool(m.remote_address), worker_spool)
			continue
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.Stop):
			return kj.Aborted()
		else:
			continue

		# Callback for on_return.
		def respond(self, response, args):
			self.send(kj.cast_to(response, self.returned_type), args.return_address)

		a = self.create(kj.GetResponse, m, worker_spool)
		self.on_return(a, respond, return_address=self.return_address)

kj.bind(server)

if __name__ == '__main__':
	kj.create(server)
