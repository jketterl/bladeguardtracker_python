import ConfigParser
from bgt.socket import Socket
from bgt.gpsd import GPSService

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	socket = Socket('wss://' + config.get('server', 'host') + '/bgt/socket');

	service = GPSService(socket, 26)
	try:
		service.start()
	except KeyboardInterrupt:
		service.stop()
		socket.close()
