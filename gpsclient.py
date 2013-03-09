import ConfigParser
from bgt.socket import Socket
from bgt.gpsd import GPSService

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	socket = Socket('wss://' + config.get('server', 'host') + '/bgt/socket');
	socket.connect();

	service = GPSService(socket, 3)
	service.start()
