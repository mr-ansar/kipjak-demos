# test_server_11.py
import kipjak as kj
from test_api import Xy

DEFAULT_ADDRESS = kj.HostPort('127.0.0.1', 5050)
SERVER_API = [Xy,]

def server(self, server_address: kj.HostPort=None, size_of_queue: int=None, responsiveness: float=None, busy_pass_rate: int=10):
	server_address = server_address or DEFAULT_ADDRESS

	kj.listen(self, server_address, http_server=SERVER_API)
	m = self.input()
	if not isinstance(m, kj.Listening):
		return m

	kj.subscribe(self, r'test-multihosting:worker-11:[-a-f0-9]+', scope=kj.ScopeOfDirectory.LAN)
	m = self.input()
	if not isinstance(m, kj.Subscribed):
		return m
	subscribed = m

	worker_spool = self.create(kj.ObjectSpool, None, size_of_queue=size_of_queue, responsiveness=responsiveness, busy_pass_rate=busy_pass_rate)

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
		elif isinstance(m, kj.NotListening):
			break
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

	# Dont clobber m
	self.send(kj.Stop(), worker_spool)
	self.select(kj.Returned)

	kj.clear_subscribed(self, subscribed)
	self.select(kj.SubscribedCleared)

	return m	# NotListening

kj.bind(server)

if __name__ == '__main__':
	kj.create(server)
