# clients_as_threads.py
import kipjak as kj
import random
from test_api import Xy, table_type
from connect_and_request_2 import ConnectAndRequest

#
DEFAULT_SERVER = kj.HostPort('127.0.0.1', 5050)

#
#
def clients_as_threads(self, thread_count: int=1,
	server_address: kj.HostPort=None,
	request_count: int=1, slow_down: float=1.0, big_table: int=100):
	self.server_address = server_address or DEFAULT_SERVER

	kj.connect(self, self.server_address, http_client='/', application_json=True)
	m = self.input()
	if not isinstance(m, kj.Connected):
		return m
	address = self.return_address

	# Callback. When a client terminates, start another one.
	def replace(self, value, args):
		if isinstance(value, kj.Busy):
			# Busy is okay.
			pass
		elif isinstance(value, kj.Faulted):
			# Dont replace. Let the number
			# of clients reduce, perhaps to
			# none.
			return

		a = self.create(ConnectAndRequest, server_address=address,
			request_count=request_count, slow_down=slow_down,
			big_table=big_table)
		self.on_return(a, replace)

	# Start with full set and setup replace callback.
	for i in range(thread_count):
		a = self.create(ConnectAndRequest, server_address=address,
			request_count=request_count, slow_down=slow_down,
			big_table=big_table)
		self.on_return(a, replace)

	# Two ways this can end - control-c and faults.
	# By default it will be because all the clients faulted.
	ending = kj.Faulted('number of clients declined to zero', 'see logs')

	while self.working():
		m = self.input()
		if isinstance(m, kj.Stop):
			self.abort()
			ending = kj.Aborted()
			break
		elif isinstance(m, kj.Returned):
			d = self.debrief()
			if isinstance(d, kj.OnReturned):
				d(self, m)

	# Wait for clearing of clients.
	while self.working():
		r = self.input()
		if isinstance(r, kj.Returned):
			d = self.debrief()
			# No callback processing.
			# Just debrief() to clear the OnReturned entry.

	return ending

kj.bind(clients_as_threads)


if __name__ == '__main__':
	kj.create(clients_as_threads)
