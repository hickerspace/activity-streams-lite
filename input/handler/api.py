#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, urllib, urllib2, json
from datetime import datetime

"""
ApiHandler implements a generic way to poll data from our API. Additional methods poll
data and insert it into the database.
"""
class ApiHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(ApiHandler, self).__init__(dbConnection)

	def api(self):
		# pseudo method to get recognized
		pass

	def apiCall(self, resource):
		apiUrl = "https://hickerspace.org/api/%s" % resource
		request = urllib2.Request(apiUrl)
		response = json.load(urllib2.urlopen(request))
		return response

	def room(self):
		status = self.apiCall("room")
		since = datetime.fromtimestamp(long(status["since"]))
		content = "Our room is %s." % status["roomStatus"]
		self.insert(since, "sensor", "room", \
			"https://hickerspace.org/wiki/Raumstatus", content)

	def matewaage(self):
		status = self.apiCall("mate-o-meter")
		updated = datetime.fromtimestamp(long(status["lastUpdate"]))

		if status["bottles"] > 1:
			content = "%d bottles left." % status["bottles"]
		elif status["bottles"] == 1:
			content = "Only 1 bottle left."
		else:
			content = "No bottles left."

		self.insert(updated, "sensor", "mate-o-meter", \
			"https://hickerspace.org/Mate-O-Meter", content)

	def trafficlight(self):
		status = self.apiCall("ampel")
		updated = datetime.fromtimestamp(long(status["lastUpdate"]))
		colors = ["red", "yellow", "green"]
		lightStatus = { True: "on", False: "off" }
		lights = [ "%s: %s" % (color, lightStatus[status[color]]) for color in colors ]
		extendedInfo = "" if status["mode"] == "random" else " (%s)" % ", ".join(lights)
		content = 'Traffic light mode switched to "%s"%s.' % (status["mode"], extendedInfo)
		self.insert(updated, "sensor", "traffic-light", \
			"https://hickerspace.org/wiki/Verkehrsampel", content)

