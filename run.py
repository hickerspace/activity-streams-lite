#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from handler.feed import FeedHandler
from handler.api import ApiHandler

sqlData = {	"host": "MYSQL_HOST",
			"user": "MYSQL_USER",
			"pass": "MYSQL_PASS",
			"db":   "MYSQL_DB" }

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
	sqlConnection = MySQLdb.connect(sqlData["host"], sqlData["user"], sqlData["pass"], sqlData["db"])

	# RSS/Atom
	feed = FeedHandler(sqlConnection)
	feed.github(githubToken)
	feed.facebook()
	feed.youtube()
	feed.wiki()
	feed.soup(soupToken)

	# Hickerspace-API
	api = ApiHandler(sqlConnection)
	api.room()
	api.matewaage()

if __name__ == "__main__":
	main()
