#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
from handler.feed import FeedHandler
from handler.api import ApiHandler
from handler.twitter import TwitterHandler
from handler.mailinglist import MailinglistHandler

config = ConfigParser.SafeConfigParser()
config.read("config")

twitterAccNames = config.get("twitter", "accountNames").split(",")
mailmanLists = config.get("mailman", "lists").split(",")

"""
Establishes a database connection and calls different handlers and their data-collecting methods.
"""
def main():
	sqlCon = MySQLdb.connect(config.get("database", "host"), config.get("database", "username"), \
		config.get("database", "password"), config.get("database", "databaseName"))

	# RSS/Atom
	feed = FeedHandler(sqlCon)
	feed.github(config.get("github", "token"))
	feed.facebook()
	feed.youtube()
	feed.wiki()
	feed.soup(config.get("soup", "token"))
	print feed.status()

	# Hickerspace-API
	api = ApiHandler(sqlCon)
	api.room()
	api.matewaage()
	print api.status()

	# Twitter-API
	twit = TwitterHandler(sqlCon, config.get("twitter", "consumerKey"), config.get("twitter", "consumerSecret"), \
		config.get("twitter", "accessToken"), config.get("twitter", "accessTokenSecret"))
	for accName in twitterAccNames:
		twit.timeline(accName)
	twit.mentions(twitterAccNames)
	print twit.status()

	# Mailinglist
	mail = MailinglistHandler(sqlCon)
	for mailmanList in mailmanLists:
		mail.posts(config.get("mailman", "weburl"), mailmanList, config.get("mailman", "loginMailAddress"), \
			config.get("mailman", "loginPassword"))
	print mail.status()


if __name__ == "__main__":
	main()
