#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb, ConfigParser, logging
from handler.feed import FeedHandler
from handler.api import ApiHandler
from handler.twitter import TwitterHandler
from handler.mailinglist import MailinglistHandler

class BaseRunner(object):
	def __init__(self):
		self.config = ConfigParser.SafeConfigParser()
		self.config.read("config")

		self.twitterAccNames = self.config.get("twitter", "accountnames").split(",")
		self.mailmanLists = self.config.get("mailman", "lists").split(",")

	def newDbConnection(self):
		conf = self.config._sections["database"]
		return MySQLdb.connect(conf["host"], conf["username"], conf["password"], \
			conf["databasename"], charset="utf8", use_unicode=True)

	def wrap(self, method):
		con = self.newDbConnection()
		obj = method(con)
		# close cursor
		obj.close()
		# close db connection
		con.close()
		logging.info("%s: %s" % (method.__name__, obj.status()))

	def github(self, con):
		feed = FeedHandler(con)
		conf = self.config._sections["github"]
		feed.githubOrga(conf["organization"], conf["user"], conf["token"])
		return feed

	def facebook(self, con):
		feed = FeedHandler(con)
		feed.facebook(self.config.get("facebook", "id"))
		return feed

	def youtube(self, con):
		feed = FeedHandler(con)
		feed.youtube(self.config.get("youtube", "user"))
		return feed

	def mediawiki(self, con):
		feed = FeedHandler(con)
		feed.mediaWiki(self.config.get("mediawiki", "feedurl"))
		return feed

	def soup(self, con):
		feed = FeedHandler(con)
		feed.soup(self.config.get("soup", "user"), self.config.get("soup", "token"))
		return feed

	def room(self, con):
		api = ApiHandler(con)
		api.room()
		return api

	def mateometer(self, con):
		api = ApiHandler(con)
		api.matewaage()
		return api

	def trafficlight(self, con):
		api = ApiHandler(con)
		api.trafficLight()
		return api

	def twitAuth(self, twit):
		conf = self.config._sections["twitter"]
		twit.auth(conf["consumerkey"], conf["consumersecret"], conf["accesstoken"], \
			conf["accesstokensecret"])
		return twit

	def twittimeline(self, con):
		twit = TwitterHandler(con)
		twit = self.twitAuth(twit)
		for accName in self.twitterAccNames:
			twit.timeline(accName)
		return twit

	def twitmentions(self, con):
		twit = TwitterHandler(con)
		twit = self.twitAuth(twit)
		twit.mentions(self.twitterAccNames)
		return twit

	def listposts(self, con):
		conf = self.config._sections["mailman"]
		mail = MailinglistHandler(con)
		for mailmanList in self.mailmanLists:
			mail.posts(conf["weburl"], mailmanList, conf["loginmailaddress"], \
				conf["loginpassword"])
		return mail

	def listsubscribers(self, con):
		conf = self.config._sections["mailman"]
		mail = MailinglistHandler(con)
		for mailmanList in self.mailmanLists:
			mail.subscribers(conf["weburl"], mailmanList, conf["loginmailaddress"], \
				conf["loginpassword"])
		return mail

