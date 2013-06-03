#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from handler.feed import FeedHandler
from handler.api import ApiHandler
from handler.twitter import TwitterHandler

# SQL data
sql = {	"host": "MYSQL_HOST",
		"user": "MYSQL_USER",
		"pass": "MYSQL_PASS",
		"db":   "MYSQL_DB" }

# Twitter credentials
twitter = {	"consumerKey": "TWITTER_CONSUMER_KEY",
			"consumerSecret": "TWITTER_CONSUMER_SECRET",
			"accessToken": "TWITTER_ACCESS_TOKEN",
			"accessTokenSecret": "TWITTER_ACCESS_TOKEN_SECRET" }

# Twitter account names
twitterAccNames = [ "TWITTER_ACCOUNT_1", "TWITTER_ACCOUNT_2" ]

"""
Switch to organization context, click on "News Feed" and copy the token:
https://github.com/organizations/hickerspace/basti2342.private.atom?token=THIS_IS_THE_TOKEN
"""
githubToken = "GITHUB_TOKEN"

"""
Go to http://www.soup.io/notifications, click on "RSS-Feed" an copy the token:
http://www.soup.io/notifications/THIS_IS_THE_TOKEN.rss
"""
soupToken = "SOUP_TOKEN"


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

	# Hickerspace-API
	api = ApiHandler(sqlCon)
	api.room()
	api.matewaage()

	# Twitter-API
	twit = TwitterHandler(sqlCon, twitter["consumerKey"], twitter["consumerSecret"], \
		twitter["accessToken"], twitter["accessTokenSecret"])
	for accName in twitterAccNames:
		twit.timeline(accName)
	twit.mentions(twitterAccNames)


if __name__ == "__main__":
	main()
