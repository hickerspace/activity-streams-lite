#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MySQLdb import IntegrityError
from time import mktime, struct_time
from datetime import datetime, timedelta
from calendar import timegm
import re, logging

"""
This class provides a basic handler. It should be extended by feed-/API-methods.
The database connection must be established before.
"""
class BaseHandler(object):
	def __init__(self, dbConnection):
		# db cursor
		self.cursor = dbConnection.cursor()
		# count new db rows
		self.newRecords = 0
		# count rows already there
		self.duplicateQueries = 0
		# the service we're handling right now
		self.service = None
		# type (like new repo, new commit in case of GitHub)
		self.type_ = None
		# the account we're handling right now
		self.account = None
		# other accounts we have for this service
		self.accounts = []

	def updateStats(self, type_=None, allTypes=False):
		# this method updates the last_update table which feeds the Flask status page
		if not type_:
			type_ = self.type_

		if allTypes:
			self.cursor.execute("SELECT type FROM last_update WHERE service=%s", (self.service,))
			types = [t[0] for t in self.cursor.fetchall()]
		else:
			types = [type_]

		for t in types:
			self.cursor.execute("INSERT INTO last_update (datetime, service, " \
				+ "type, account, error) VALUES (%s, %s, %s, %s, %s) ON " \
				+ "DUPLICATE KEY UPDATE datetime=VALUES(datetime), " \
				+ "error=VALUES(error)", (datetime.now(), self.service, t, \
				self.account, False))

	def __getNotUpdatedTypes(self):
		# returns types that have not been updated in the last 60 seconds
		types = []
		self.cursor.execute("SELECT type, datetime FROM last_update WHERE " \
			+ "service = %s", (self.service,))
		for type_, date in self.cursor:
			if date < datetime.now() - timedelta(seconds=60):
				types.append(type_)
		return types


	def setError(self):
		# mark not recently updated types and use dummy date (because we do
		# not have a better guess)
		for type_ in self.__getNotUpdatedTypes():
			self.cursor.execute("INSERT INTO last_update (datetime, service, " \
				+ "type, account, error) VALUES (%s, %s, %s, %s, %s) ON " \
				+ "DUPLICATE KEY UPDATE error=VALUES(error)", \
				(datetime(1970, 1, 1, 0, 0), self.service, type_, \
				self.account, True))

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

		# remove multiple spaces in content
		content = re.sub('\s{2,}', ' ', content)

		try:
			# insert activity into table
			self.cursor.execute("INSERT INTO activities (datetime, person, " \
				"service, type, account, content, url) VALUES (%s, %s, %s, " \
				"%s, %s, %s, %s)", (date, person, self.service, self.type_, \
				self.account, content, url))

			self.newRecords += 1
		except IntegrityError as e:
			# duplicate entry
			if e.args[0] == 1062:
				self.duplicateQueries += 1
			else:
				self.log("Last SQL statement: %s" % self.cursor._last_executed)
				# this will be caught somewhere else
				raise e

	def utcStruct2localDatetime(self, timeTuple):
		return datetime.fromtimestamp(timegm(timeTuple))

	def do(self, method, **args):
		# wrapper method that calls the method, updates the status and does
		# error handling/logging
		try:
			method(**args)
			self.updateStats()
		except Exception as e:
			self.setError()
			self.logError(e)

	def logError(self, e):
		logging.error("%s: %s - %s" % (self.__class__.__name__, e.__class__.__name__, e))

	def log(self, msg):
		logging.info("%s: %s" % (self.__class__.__name__, msg))

	def close(self):
		self.cursor.close()

	def status(self):
		# status message for logging purposes
		return "%d new record(s); %d duplicate(s)" % (self.newRecords, self.duplicateQueries)

