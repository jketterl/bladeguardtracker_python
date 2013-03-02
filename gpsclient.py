import gps, json
from ws4py.client.threadedclient import WebSocketClient

class BGTSocket(WebSocketClient):
	def received_message(self, message):
		print message

if __name__ == '__main__':
	session = gps.gps()
	session.stream(flags=gps.WATCH_JSON)

	socket = BGTSocket('wss://ec2-79-125-69-76.eu-west-1.compute.amazonaws.com/bgt/socket');
	socket.connect();

	for data in session:
		if not 'lat' in data or not 'lon' in data or not 'speed' in data: continue
		print "lat: %f, lon: %f, speed: %f" % (data.lat, data.lon, data.speed);

		socket.send(json.dumps({'command':'log','data':{'lat':data.lat,'lon':data.lon,'speed':data.speed,'eventId':3}}))
