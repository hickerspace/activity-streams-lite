#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, feedparser, re

"""
FeedHandler parses feeds and inserts particular parts into the database.
"""
class FeedHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(FeedHandler, self).__init__(dbConnection)

	def github(self):
		# new repos have to be inserted manually
		urls = ["https://github.com/hickerspace/ledticker/commits/master.atom",
				"https://github.com/hickerspace/Bahnanzeige/commits/master.atom",
				"https://github.com/hickerspace/REST-API/commits/master.atom",
				"https://github.com/hickerspace/Mensabot/commits/master.atom",
				"https://github.com/hickerspace/Mate-O-Meter/commits/master.atom",
				"https://github.com/hickerspace/Community-Twitter/commits/master.atom",
				"https://github.com/hickerspace/microprinting/commits/master.atom",
				"https://github.com/hickerspace/Ampelschaltung/commits/master.atom",
				"https://github.com/hickerspace/API-Examples/commits/master.atom"]

		for url in urls:
			feed = feedparser.parse(url)
			for entry in feed["entries"]:
				self.insert(entry["updated_parsed"], "GitHub", "Commit", entry["link"], \
					"%s: %s" % (feed["feed"]["title"], entry["title"]), entry["author"])

	def facebook(self):
		urls = ["http://www.facebook.com/feeds/page.php?format=atom10&id=148681465224497"]

		for url in urls:
			feed = feedparser.parse(url)
			for entry in feed["entries"]:
				# strip html
				cleanContent = re.sub('<[^<]+?>', '', entry["content"][0]["value"])
				self.insert(entry["updated_parsed"], "Facebook", "Pinnwand", entry["link"], cleanContent)

	def youtube(self):
		urls = ["http://gdata.youtube.com/feeds/base/users/hickerspace/uploads?alt=rss&v=2&orderby=published"]
		service = "YouTube"
		for url in urls:
			# get videos
			feed = feedparser.parse(url)
			for entry in feed["entries"]:
				self.insert(entry["updated_parsed"], service, "Video", entry["link"], entry["title"])

			# get comments
			for entry in feed["entries"]:
				id = re.findall(r"v=(.*)[&$]", entry["link"])[0]
				title = entry["title"]
				link = "http://www.youtube.com/all_comments?v=%s" % id

				commentFeed = feedparser.parse("https://gdata.youtube.com/feeds/api/videos/%s/comments" % id)
				for commentEntry in commentFeed["entries"]:
					content = 'Kommentar zu "%s": %s' % (title, commentEntry["subtitle"]
						.encode("latin-1", "ignore"))
					self.insert(entry["updated_parsed"], service, "Kommentar", link, content)

