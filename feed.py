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
		private = ["https://github.com/organizations/hickerspace/basti2342.private.atom?token=PASTE_TOKEN_HERE"]

		for url in private:
			feed = feedparser.parse(url)
			for entry in feed["entries"]:
				type = "Activity"
				# try to get the specific event from the id
				typeMatch = re.findall(r"^tag:github.com,2008:(.*?)Event/\d+$", entry["id"])
				if typeMatch:
					type = typeMatch[0]

				self.insert(entry["updated_parsed"], "GitHub", type, entry["link"], \
					entry["title"], entry["author"])

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

	def wiki(self):
		urls = ["http://hickerspace.org/w/index.php?title=Spezial:Letzte_%C3%84nderungen&feed=atom"]

		for url in urls:
			feed = feedparser.parse(url)
			for entry in feed["entries"]:
				# try to parse edit summary
				summaryMatch = re.findall(r"^<p>(.+?)</p>", entry["summary"])
				# strip html
				summary = ": %s" % re.sub('<[^<]+?>', '', summaryMatch[0]) if summaryMatch else ""
				content = "%s%s" % (entry["title"], summary)

				self.insert(entry["updated_parsed"], "Wiki", "Activity", entry["link"], \
					content.encode("latin-1", "ignore"), entry["author"])

