from ws4py.client.threadedclient import WebSocketClient
import json, threading
from .command import Command

class Socket(object):
	def __init__(self, url, eventId):
		self.client = None
		self.url = url
		self.eventId = eventId
	def send(self, command):
		self.getClient().send(command.getJson())
	def getClient(self):
		if self.client is None:
			self.client = Client(self.url, self)
			self.send(Command('subscribeUpdates', {'eventId':26, 'category':['stats']}))
		return self.client
	def close(self):
		if self.client is None: return
		self.client.close()
	def onClose(self, client):
		if client is not self.client: return
		self.client = None

class Client(WebSocketClient):
	def __init__(self, url, socket):
		self.socket = socket
		self.queue = []
		self.open = False
		super(Client, self).__init__(url)
		self.connect()
	def opened(self):
		print "connected"
		self.resetTimeout()
		self.speed = None
		self.distance = None
		self.open = True
		self.send(Command('auth', {'user':'raspi01','pass':'bgtisc00l'}).getJson());
		for command in self.queue:
			self.send(command)
		self.queue = []
		#self.send(Command('subscribeUpdates', {'eventId':26, 'category':['stats']}).getJson())
	def closed(self, code, reason = None):
		print "connection closed"
		print reason
		self.cancelTimeout()
		self.socket.onClose(self)
	def send(self, message):
		if (self.open): return super(Client, self).send(message)
		self.queue.append(message)
	def cancelTimeout(self):
		if hasattr(self, 'timeout'):
			self.timeout.cancel()
	def resetTimeout(self):
		def timeout():
			print "socket timeout!"
			self.close()
		self.cancelTimeout()
		self.timeout = threading.Timer(30, timeout)
		self.timeout.start()
	def received_message(self, message):
		message = json.loads(str(message))
		if 'event' in message and message['event'] == 'update':
			stats = message['data']['stats'][0]
			if 'bladeNightSpeed' in stats:
				self.speed = stats['bladeNightSpeed']
			else:
				self.speed = None
		else:
			if \
				'data' in message and \
				'locked' in message['data'] and \
				message['data']['locked'] and \
				'distanceToEnd' in message['data']:
					self.distance = message['data']['distanceToEnd']
			else:
				self.distance = None

		self.calculateStats()

	def process(self, bytes):
		# process means we received something. since the server will send a ping after at most 20 seconds
		# we can use this as an indicator, that the connection is still alive.
		self.resetTimeout()
		return super(Client, self).process(bytes)
	def calculateStats(self):
		if self.distance is not None and self.speed is not None:
			print "noch %d minuten!" % int(round(self.distance * 1000 / self.speed / 60))
		else:
			print "Keine Angabe moeglich"

