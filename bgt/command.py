import json

class Command(object):
	def __init__(self, command, data = None):
		self.command = command
		self.data = data
	def getJson(self):
		return json.dumps({'command':self.command, 'data':self.data})
