#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MySQLdb import IntegrityError
from time import mktime, struct_time
from datetime import datetime
from calendar import timegm
import re

"""
This class provides a basic handler. It should be extended by feed-/API-methods.
The database connection must be established before.
"""
class BaseHandler(object):
	def __init__(self, dbConnection):
		self.cursor = dbConnection.cursor()
		self.newRecords = 0
		self.duplicateQueries = 0
		self.service = None
		self.type_ = None
		self.account = None

	def setAccount(self, account):
		self.account = account

	def updateStats(self, type_=None):
		if not type_:
			type_ = self.type_
		self.cursor.execute("INSERT INTO last_update (datetime, service, type, account, error) " \
			+ "VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE datetime=VALUES(datetime), error=VALUES(error)", \
			(datetime.now(), self.service, type_, self.account, False))

	def setError(self):
		self.cursor.execute("INSERT INTO last_update (datetime, service, type, account, error) VALUES " \
			+ "(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE error=VALUES(error)", \
			(datetime(1970, 1, 1, 0, 0), self.service, self.type_, self.account, True))

	def insert(self, date, url="", content="", person=""):
		if not self.account:
			raise ValueError("No account set.")

		# convert date to SQL DATETIME
		if isinstance(date, struct_time):
			date = self.utcStruct2localDatetime(date)
		if isinstance(date, datetime):
			date = date.strftime("%Y-%m-%d %H:%M:%S")
		else:
			raise TypeError("Unknown date format.")

		# remove multiple spaces
		content = re.sub('\s{2,}', ' ', content)

		try:
			self.cursor.execute("INSERT INTO activities (datetime, person, service, type, " \
				+ "account, content, url) VALUES (%s, %s, %s, %s, %s, %s, %s)", (date, person, \
				self.service, self.type_, self.account, content, url))

			self.newRecords += 1
		except IntegrityError as e:
			# duplicate entry
			if e.args[0] == 1062:
				self.duplicateQueries += 1
				#print e.args[1]
			else:
				print "Last SQL statement: %s" % self.cursor._last_executed
				raise e

	def utcStruct2localDatetime(self, timeTuple):
		return datetime.fromtimestamp(timegm(timeTuple))

	def close(self):
		self.cursor.close()

	def status(self):
		return "%d new record(s); %d duplicate(s)" % (self.newRecords, self.duplicateQueries)
