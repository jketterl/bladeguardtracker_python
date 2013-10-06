import smbus, serial, time

class Output(object):
	def write(self, minutes):
		pass
	def reset(self):
		pass

class ConsoleOutput(Output):
	def write(self, minutes):
		if minutes is None:
			print "Keine Angabe moeglich"
		else:
			print "noch %d minuten!" % minutes

class SerialOutput(Output):
	def __init__(self, *args, **kwargs):
		super(Output, self).__init__(*args, **kwargs)
		self.ser = serial.Serial('/dev/ttyACM0', 9600)
	def write(self, minutes):
		if minutes is None:
			self.ser.write('NO DATA\n')
		else:
			self.ser.write('NOCH %d MINUTEN\n' % minutes)
		self.ser.flush()
		self.ser.flushInput()

class SPIOutput(Output):
	def __init__(self, *args, **kwargs):
		super(Output, self).__init__(*args, **kwargs)
	def write(self, minutes):
		print minutes
		out = open('/dev/spidev0.0', 'w')
		if minutes is None:
			out.write('NO DATA \n')
		else:
			out.write('NOCH %d MINUTEN\n' % minutes)
		out.close()
	def reset(self):
		out = open('/dev/spidev0.0', 'w')
		out.write('RESET\n')

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
