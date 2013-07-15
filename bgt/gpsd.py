import json, gps, threading
from .command import Command

class GPSService(object):
	def __init__(self, socket, eventId):
		self.socket = socket
		self.locked = False
		self.gpsOn = False
		self.eventId = eventId
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
			self.socket.send(Command('log', {'lat':data.lat,'lon':data.lon,'speed':data.speed,'eventId':self.eventId}))

			self.resetSignalTimeout()
	def stop(self):
		self.cancelGPSTimeout()
		self.cancelSignalTimeout()
	def cancelGPSTimeout(self):
		if (hasattr(self, 'gpstimeout')):
			self.gpstimeout.cancel();
	def resetGPSTimeout(self):
		def timeout():
			self.locked = False
		self.cancelGPSTimeout()
		self.gpstimeout = threading.Timer(5, timeout)
		self.gpstimeout.start()
	def cancelSignalTimeout(self):
		if (hasattr(self, 'signaltimeout')):
			self.signaltimeout.cancel();
	def resetSignalTimeout(self):
		def timeout():
			self.sendGPSUnavailable()
		self.cancelSignalTimeout()
		self.signaltimeout = threading.Timer(60, timeout)
		self.signaltimeout.start()
	def sendGPSUnavailable(self):
		if not self.gpsOn: return
		self.gpsOn = False
		self.socket.send(Command('gpsUnavailable', {'eventId':self.eventId}))
