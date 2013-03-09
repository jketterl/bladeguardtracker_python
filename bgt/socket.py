from ws4py.client.threadedclient import WebSocketClient
import json, threading

class Socket(WebSocketClient):
	def opened(self):
		print "connected"
		self.resetTimeout()
		self.speed = None
		self.distance = None
	def closed(self, code, reason = None):
		print "connection closed"
		print reason
	def resetTimeout(self):
		def timeout():
			print "socket timeout!"
		if hasattr(self, 'timeout'):
			self.timeout.cancel()
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
		return super(Socket, self).process(bytes)
	def calculateStats(self):
		if self.distance is not None and self.speed is not None:
			print "noch %d minuten!" % int(round(self.distance * 1000 / self.speed / 60))
		else:
			print "Keine Angabe moeglich"

