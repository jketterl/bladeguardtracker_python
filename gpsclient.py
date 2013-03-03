import gps, json, ConfigParser, threading
from ws4py.client.threadedclient import WebSocketClient

class BGTSocket(WebSocketClient):
	def opened(self):
		print "connected"
		self.resetTimeout()
	def resetTimeout(self):
		def timeout():
			print "timeout!"
		if hasattr(self, 'timeout'):
			self.timeout.cancel()
		self.timeout = threading.Timer(30, timeout)
		self.timeout.start()
	def received_message(self, message):
		print message
	def process(self, bytes):
		# process means we received something. since the server will send a ping after at most 20 seconds
		# we can use this as an indicator, that the connection is still alive.
		self.resetTimeout()
		return super(BGTSocket, self).process(bytes)

class BGTGPSService(object):
	def __init__(self, socket):
		self.socket = socket
		self.locked = False
	def start(self):
		session = gps.gps()
		session.stream(flags=gps.WATCH_JSON)
		
		for data in session:
			if not 'lat' in data or not 'lon' in data or not 'speed' in data: continue
			
			if self.locked: continue
			self.locked = True
			self.resetGPSTimeout()

			print "lat: %f, lon: %f, speed: %f" % (data.lat, data.lon, data.speed);

			self.socket.send(json.dumps({'command':'log','data':{'lat':data.lat,'lon':data.lon,'speed':data.speed,'eventId':3}}))
	def resetGPSTimeout(self):
		def timeout():
			self.locked = False
		if (hasattr(self, 'gpstimeout')):
			self.gpstimeout.cancel();
		self.gpstimeout = threading.Timer(5, timeout)
		self.gpstimeout.start()

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	socket = BGTSocket('wss://' + config.get('server', 'host') + '/bgt/socket');
	socket.connect();

	service = BGTGPSService(socket)
	service.start()
