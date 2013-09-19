import smbus

class Output(object):
	def write(self, minutes):
		pass

class ConsoleOutput(Output):
	def write(self, minutes):
		if minutes is None:
			print "Keine Angabe moeglich"
		else:
			print "noch %d minuten!" % minutes

class LEDOutput(Output):
	dash = 0b00001000
	numbers = [
		0b01110111,
		0b01000100,
		0b01101011,
		0b11101110,
		0b01011100,
		0b00111110,
		0b00111111,
		0b01100100,
		0b01111111,
		0b01111110,
	]
	def __init__(self):
		self.bus = smbus.SMBus(1)
		self.addr = 0x38
		# init sequence
		self.send(0x00, 0x20)
		self.clear()
	def clear(self):
		# show "no data available"
		self.send(0x01, self.dash)
		self.send(0x02, self.dash)
	def show(self, num):
		# can't show anything bigger than 100
		num %= 100
		self.send(0x01, self.numbers[num / 10])
		self.send(0x02, self.numbers[num % 10])
	def send(self, reg, data):
		self.bus.write_byte_data(self.addr, reg, data)
	def write(self, minutes):
		if minutes is None:
			self.clear()
		else:
			self.show(minutes)
