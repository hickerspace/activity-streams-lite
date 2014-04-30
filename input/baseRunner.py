#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb, ConfigParser, logging
from os.path import join, dirname
from handler.base import BaseHandler

"""
Base runner inherits to activity scheduler and provides db connection, wrapper
methods for handler and error handling.
"""
class BaseRunner(object):
	def __init__(self):
		# parse config and provide it as class variable
		self.config = ConfigParser.SafeConfigParser()
		self.config.read(join(dirname(__file__), "config"))

		# create a service-accounts-dictionary
		self.accounts = dict((s, a.split(",")) for (s, a) in \
			self.config._sections["accounts"].items())

		print self.accounts

	def newDbConnection(self):
		# open new db connection
		conf = self.config._sections["database"]
		return MySQLdb.connect(conf["host"], conf["username"], conf["password"], \
			conf["databasename"], charset="utf8", use_unicode=True)

	def callHandler(self, methodName, dbCon):
		# iterate over classes inheriting from base handler (all other handlers)
		for handler in BaseHandler.__subclasses__():
			# if handler has method with given name, call it with db connection
			if callable(getattr(handler, methodName, None)):
				return handler(dbCon)

	def handleError(self, e, obj, methodName, account):
		# log missing config sections and log other errors and mark them for
		# the flask status page (output)
		if isinstance(e, (UnboundLocalError)):
			logging.error("No config section found: %s_%s" % (methodName, account))
		else:
			obj.setError()
			logging.error("%s: %s" % (e.__class__.__name__, e))

	def wrap(self, methodName):
		# create db connection
		con = self.newDbConnection()
		# call handler (constructor) using wrapper method with db connection
		obj = self.callHandler(methodName, con)

		# iterate accounts
		for account in self.accounts[methodName]:
			try:
				conf = self.config._sections["%s_%s" % (methodName, account)]
				del conf["__name__"]
			except KeyError:
				# no config section found (normal in case method needs no arguments)
				pass

			# set account
			obj.account = account
			# set all other accounts on this service (which is similar to methodName)
			obj.accounts = self.accounts[methodName]

			try:
				try:
					# try to call handler method named as the service with config
					obj.do(getattr(obj, methodName), **conf)
				except UnboundLocalError:
					# mh, this failed, now try without config (because some handlers
					# do not expect configs)
					obj.do(getattr(obj, methodName))
			except UnboundLocalError:
				# meh, this failed too, log it and go on
				logging.error("No config section found: %s_%s" % (methodName, account))

		# close cursor
		obj.close()
		# close db connection
		con.close()
		logging.info("%s - %s" % (methodName, obj.status()))

