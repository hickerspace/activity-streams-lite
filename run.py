#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf import *
import MySQLdb
from handler.feed import FeedHandler
from handler.api import ApiHandler
from handler.twitter import TwitterHandler
from handler.mailinglist import MailinglistHandler

"""
Establishes a database connection and calls different handlers and their data-collecting methods.
"""
def main():
	sqlCon = MySQLdb.connect(sql["host"], sql["user"], sql["pass"], sql["db"])

	# RSS/Atom
	feed = FeedHandler(sqlCon)
	feed.github(githubToken)
	feed.facebook()
	feed.youtube()
	feed.wiki()
	feed.soup(soupToken)
	print feed.status()

	# Hickerspace-API
	api = ApiHandler(sqlCon)
	api.room()
	api.matewaage()
	print api.status()

	# Twitter-API
	twit = TwitterHandler(sqlCon, twitter["consumerKey"], twitter["consumerSecret"], \
		twitter["accessToken"], twitter["accessTokenSecret"])
	for accName in twitterAccNames:
		twit.timeline(accName)
	twit.mentions(twitterAccNames)
	print twit.status()

	# Mailinglists
	mail = MailinglistHandler(sqlCon)
	for mailmanList in mailmanLists:
		mail.posts(mailmanUrl, mailmanList, mailAddress, mailPassword)
	print mail.status()


if __name__ == "__main__":
	main()
