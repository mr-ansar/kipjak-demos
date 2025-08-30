# connect_and_request.py
import kipjak as kj
import random
from test_api import Xy, table_type

#
random.seed()

# Client As Thread.
class ConnectAndRequest(kj.Threaded, kj.Stateless):
	def __init__(self, server_address: kj.Address=None,
			request_count: int=1, slow_down: float=0.5, big_table: int=100):
		kj.Threaded.__init__(self)
		kj.Stateless.__init__(self)
		self.server_address = server_address
		self.request_count = request_count
		self.slow_down = slow_down
		self.big_table = big_table

		self.sent = None
	
	def send_request(self):
		'''Connection is active. Initiate request-response sequence.'''
		x = random.randint(1, self.big_table)
		y = random.randint(1, self.big_table)
		xy = Xy(x, y)
		self.send(xy, self.server_address)
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
			self.complete(kj.Ack())

		# Take a breath.
		s = kj.spread_out(self.slow_down)
		self.start(kj.T1, s)

def ConnectAndRequest_Start(self, message):
	self.send_request()

def ConnectAndRequest_list_list_float(self, message):	# Expected table.
	self.post_response(message)

def ConnectAndRequest_Busy(self, message):	# Fault processing in the parent.
	self.request_count -= 1
	if self.request_count < 1:
		self.complete(kj.Ack())

	s = kj.spread_out(self.slow_down)
	self.start(kj.T1, s)

def ConnectAndRequest_T1(self, message):				# Breather over.
	self.send_request()

def ConnectAndRequest_Stop(self, message):
	self.complete(kj.Aborted())

def ConnectAndRequest_Faulted(self, message):	# Fault processing in the parent.
	self.complete(message)

#
#
CONNECT_AND_REQUEST_DISPATCH = (
	kj.Start,
	table_type, kj.Busy, kj.T1,
	kj.Stop,
	kj.Faulted,
)

kj.bind(ConnectAndRequest,
	CONNECT_AND_REQUEST_DISPATCH,
	return_type=kj.Any())
