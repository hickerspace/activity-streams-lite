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

