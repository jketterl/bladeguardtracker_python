import gps, json, ConfigParser
from ws4py.client.threadedclient import WebSocketClient

class BGTSocket(WebSocketClient):
	def received_message(self, message):
		print message

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	session = gps.gps()
	session.stream(flags=gps.WATCH_JSON)

	socket = BGTSocket('wss://' + config.get('server', 'host') + '/bgt/socket');
	socket.connect();

	for data in session:
		if not 'lat' in data or not 'lon' in data or not 'speed' in data: continue
		print "lat: %f, lon: %f, speed: %f" % (data.lat, data.lon, data.speed);

		socket.send(json.dumps({'command':'log','data':{'lat':data.lat,'lon':data.lon,'speed':data.speed,'eventId':3}}))
