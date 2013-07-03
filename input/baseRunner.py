#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb, ConfigParser, logging
from handler.feed import FeedHandler
from handler.api import ApiHandler
from handler.twitter import TwitterHandler
from handler.mailinglist import MailinglistHandler

HANDLER = [ FeedHandler, ApiHandler, TwitterHandler, MailinglistHandler ]

class BaseRunner(object):
	def __init__(self):
		self.config = ConfigParser.SafeConfigParser()
		self.config.read("config")

		# create a service-accounts-dictionary
		self.accounts = dict((s, a.split(",")) for (s, a) in self.config._sections["accounts"].items())

	def newDbConnection(self):
		conf = self.config._sections["database"]
		return MySQLdb.connect(conf["host"], conf["username"], conf["password"], \
			conf["databasename"], charset="utf8", use_unicode=True)

	def wrap(self, methodName):
		con = self.newDbConnection()
		for h in HANDLER:
			if callable(getattr(h, methodName, None)):
				obj = h(con)

		for account in self.accounts[methodName]:
			try:
				conf = self.config._sections["%s_%s" % (methodName, account)]
				del conf["__name__"]
			except KeyError:
				# no config section found
				pass

			obj.setAccount(account)
			try:
				if methodName == "api":
					obj.room()
					obj.matewaage()
					obj.trafficlight()
				elif methodName == "twitter":
					obj.auth(**conf)
					obj.timeline(account)
					obj.mentions(self.accounts[methodName])
				elif methodName == "mailman":
					obj.posts(**conf)
					obj.subscribers(**conf)
				else:
					getattr(obj, methodName)(**conf)
			except UnboundLocalError:
				logging.error("No config section found: %s_%s" % (methodName, account))
		# close cursor
		obj.close()
		# close db connection
		con.close()
		logging.info("%s: %s" % (methodName, obj.status()))

