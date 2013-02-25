import gps

if __name__ == '__main__':
	session = gps.gps()
	session.stream(flags=gps.WATCH_JSON)

	for data in session:
		if not 'lat' in data or not 'lon' in data or not 'speed' in data: continue
		print "lat: %f, lon: %f, speed: %f" % (data.lat, data.lon, data.speed);
