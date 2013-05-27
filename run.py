#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from feed import FeedHandler
from api import ApiHandler

sqlData = {	"host": "MYSQL_HOST",
			"user": "MYSQL_USER",
			"pass": "MYSQL_PASS",
			"db":   "MYSQL_DB" }

"""
Establishes a database connection and calls different handlers and their data-collecting methods.
"""
def main():
	sqlConnection = MySQLdb.connect(sqlData["host"], sqlData["user"], sqlData["pass"], sqlData["db"])

	# RSS/Atom
	feed = FeedHandler(sqlConnection)
	feed.github()
	feed.facebook()
	feed.youtube()

	# Hickerspace-API
	api = ApiHandler(sqlConnection)
	api.room()
	api.matewaage()

if __name__ == "__main__":
	main()
