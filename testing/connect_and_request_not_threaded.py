# connect_and_request_not_threaded.py
import kipjak as kj
import random
from test_api import Xy, table_type

#
random.seed()

#
DEFAULT_SERVER = kj.HostPort('127.0.0.1', 5050)

class ConnectAndRequest(kj.Point, kj.Stateless):
	def __init__(self, server_address: kj.HostPort=None,
			request_count: int=1, slow_down: float=0.5, big_table: int=100):
		kj.Point.__init__(self)
		kj.Stateless.__init__(self)
		self.server_address = server_address or DEFAULT_SERVER
		self.request_count = request_count
		self.slow_down = slow_down
		self.big_table = big_table

		self.sent = None
		self.client_address = None
	
	def send_request(self):
		'''Connection is active. Initiate request-response sequence.'''
		x = random.randint(1, self.big_table)
		y = random.randint(1, self.big_table)
		xy = Xy(x, y)
		self.send(xy, self.client_address)
		self.sent = xy

	def post_response(self, response):
		'''Response received, validate and determine next move.'''
		y = len(response)
		x = len(response[0])

		sent = self.sent
		if not (x == sent.x and y == sent.y):
			self.complete(kj.Faulted('not the matching table'))

		# Completed sequence of requests.
		self.request_count -= 1
		if self.request_count < 1:
			self.send(kj.Close(), self.client_address)
			return

		# Take a breath.
		s = kj.spread_out(self.slow_down)
		self.start(kj.T1, s)

def ConnectAndRequest_Start(self, message):
	kj.connect(self, self.server_address, http_client='/', application_json=True)

def ConnectAndRequest_Connected(self, message):
	self.client_address = self.return_address
	self.send_request()

def ConnectAndRequest_NotConnected(self, message):
	self.complete(message)

def ConnectAndRequest_list_list_float(self, message):
	self.post_response(message)

def ConnectAndRequest_Busy(self, message):
	self.request_count -= 1
	if self.request_count < 1:
		self.send(kj.Close(), self.client_address)
		return

	s = kj.spread_out(self.slow_down)
	self.start(kj.T1, s)

def ConnectAndRequest_T1(self, message):
	self.send_request()

def ConnectAndRequest_Closed(self, message):
	self.complete(kj.Ack())

def ConnectAndRequest_Stop(self, message):
	self.complete(kj.Aborted())

def ConnectAndRequest_Faulted(self, message):
	self.complete(message)

#
#
CONNECT_AND_REQUEST_DISPATCH = (
	kj.Start,
	kj.Connected, kj.NotConnected,
	table_type, kj.Busy, kj.T1,
	kj.Closed,
	kj.Stop,
	kj.Faulted,
)

kj.bind(ConnectAndRequest,
	CONNECT_AND_REQUEST_DISPATCH,
	return_type=kj.Any())

if __name__ == '__main__':
	kj.create(ConnectAndRequest)
