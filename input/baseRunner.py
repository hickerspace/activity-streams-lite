#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb, ConfigParser, logging
from os.path import join, dirname
from handler.base import BaseHandler

class BaseRunner(object):
	def __init__(self):
		self.config = ConfigParser.SafeConfigParser()
		self.config.read(join(dirname(__file__), "config"))

		# create a service-accounts-dictionary
		self.accounts = dict((s, a.split(",")) for (s, a) in self.config._sections["accounts"].items())

	def newDbConnection(self):
		conf = self.config._sections["database"]
		return MySQLdb.connect(conf["host"], conf["username"], conf["password"], \
			conf["databasename"], charset="utf8", use_unicode=True)

	def callHandler(self, methodName, dbCon):
		for handler in BaseHandler.__subclasses__():
			if callable(getattr(handler, methodName, None)):
				return handler(dbCon)

	def handleError(self, e, obj, methodName, account):
		if isinstance(e, (UnboundLocalError)):
			logging.error("No config section found: %s_%s" % (methodName, account))
		else:
			obj.setError()
			logging.error("%s: %s" % (e.__class__.__name__, e))

	def wrap(self, methodName):
		con = self.newDbConnection()
		obj = self.callHandler(methodName, con)

		for account in self.accounts[methodName]:
			try:
				conf = self.config._sections["%s_%s" % (methodName, account)]
				del conf["__name__"]
			except KeyError:
				# no config section found (normal in case method needs no arguments)
				pass

			obj.account = account
			obj.accounts = self.accounts[methodName]

			try:
				try:
					obj.do(getattr(obj, methodName), **conf)
				except UnboundLocalError:
					obj.do(getattr(obj, methodName))
			except UnboundLocalError:
				logging.error("No config section found: %s_%s" % (methodName, account))

		# close cursor
		obj.close()
		# close db connection
		con.close()
		logging.info("%s - %s" % (methodName, obj.status()))

