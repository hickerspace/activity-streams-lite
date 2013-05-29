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

	def apiCall(self, resource):
		apiUrl = "https://hickerspace.org/api/%s" % resource
		request = urllib2.Request(apiUrl)
		response = json.load(urllib2.urlopen(request))
		return response

	def room(self):
		status = self.apiCall("room")
		since = datetime.fromtimestamp(long(status["since"]))
		statusStr = "offen" if status["roomStatus"] == "open" else "geschlossen"
		content = "Unser Raum ist %s." % statusStr
		self.insert(since, "Sensorik", "Raumstatus", \
			"https://hickerspace.org/wiki/Raumstatus", content)

	def matewaage(self):
		status = self.apiCall("mate-o-meter")
		updated = datetime.fromtimestamp(long(status["lastUpdate"]))

		if status["bottles"] > 1:
			content = "Es sind noch %d Flaschen in unserer Kiste."
		elif status["bottles"] == 1:
			content = "Es ist nur noch 1 Flasche in unserer Kiste."
		else:
			content = "Es sind keine Flaschen mehr in unserer Kiste."

		self.insert(updated, "Sensorik", "Matewaage", \
			"https://hickerspace.org/Mate-O-Meter", content)

