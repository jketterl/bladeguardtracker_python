import gps, json, ConfigParser, threading
from ws4py.client.threadedclient import WebSocketClient

class BGTSocket(WebSocketClient):
	def opened(self):
		print "connected"
		self.resetTimeout()
		self.speed = None
		self.distance = None
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
		return super(BGTSocket, self).process(bytes)
	def calculateStats(self):
		if self.distance is not None and self.speed is not None:
			print "noch %d minuten!" % int(round(self.distance * 1000 / self.speed / 60))
		else:
			print "Keine Angabe moeglich"
		

class BGTGPSService(object):
	def __init__(self, socket, eventId):
		self.socket = socket
		self.locked = False
		self.gpsOn = False
		self.eventId = eventId

		socket.send(json.dumps({'command':'subscribeUpdates','data':{'eventId':self.eventId,'category':['stats']}}))
	def start(self):
		session = gps.gps()
		session.stream(flags=gps.WATCH_JSON)
		
		for data in session:
			if data['class'] != 'TPV': continue

			if not 'lat' in data or not 'lon' in data or not 'speed' in data:
				self.sendGPSUnavailable()
				continue
			
			if self.locked: continue
			self.locked = True
			self.resetGPSTimeout()

			self.gpsOn = True
			#print "lat: %f, lon: %f, speed: %f" % (data.lat, data.lon, data.speed);
			self.socket.send(json.dumps({'command':'log','data':{'lat':data.lat,'lon':data.lon,'speed':data.speed,'eventId':self.eventId}}))

			self.resetSignalTimeout()
	def resetGPSTimeout(self):
		def timeout():
			self.locked = False
		if (hasattr(self, 'gpstimeout')):
			self.gpstimeout.cancel();
		self.gpstimeout = threading.Timer(5, timeout)
		self.gpstimeout.start()
	def resetSignalTimeout(self):
		def timeout():
			self.sendGPSUnavailable()
		if (hasattr(self, 'signaltimeout')):
			self.signaltimeout.cancel();
		self.signaltimeout = threading.Timer(60, timeout)
		self.signaltimeout.start()
	def sendGPSUnavailable(self):
		if not self.gpsOn: return
		self.gpsOn = False
		self.socket.send(json.dumps({'command':'gpsUnavailable','data':{'eventId':self.eventId}}))

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	socket = BGTSocket('wss://' + config.get('server', 'host') + '/bgt/socket');
	socket.connect();

	service = BGTGPSService(socket, 3)
	service.start()
