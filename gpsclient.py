import ConfigParser
from bgt.socket import Socket
from bgt.gpsd import GPSService
from bgt.output import LEDOutput

if __name__ == '__main__':
	config = ConfigParser.ConfigParser();
	config.read('config.ini');

	eventId = config.get('event', 'id')

	output = LEDOutput()

	socket = Socket('wss://' + config.get('server', 'host') + '/bgt/socket', eventId, output);

	service = GPSService(socket, eventId)
	try:
		service.start()
	except KeyboardInterrupt:
		service.stop()
		socket.close()
