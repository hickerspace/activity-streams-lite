#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MySQLdb import IntegrityError
from time import mktime, struct_time
from datetime import datetime

"""
This class provides a basic handler. It should be extended by feed-/API-methods.
The database connection must be established before.
"""
class BaseHandler(object):
	def __init__(self, dbConnection):
		self.cursor = dbConnection.cursor()

	def insert(self, date, service, type, url="", content="", person=""):
		if isinstance(date, struct_time):
			date = datetime.fromtimestamp(mktime(date))
		if isinstance(date, datetime):
			date = date.strftime("%Y-%m-%d %H:%M:%S")
		else:
			raise TypeError("Unknown date format.")

		try:
			self.cursor.execute("INSERT INTO activities (datetime, person, service, type, " \
				+ "content, url) VALUES (%s, %s, %s, %s, %s, %s)", (date, person, service, \
				type, content, url))
		except IntegrityError as e:
			# duplicate entry
			if e.args[0] == 1062:
				print e.args[1]
			else:
				print "Last SQL statement: %s" % self.cursor._last_executed
				raise e

