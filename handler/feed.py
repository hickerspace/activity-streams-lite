#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, feedparser, re, json

"""
FeedHandler parses feeds and inserts particular parts into the database.
"""
class FeedHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(FeedHandler, self).__init__(dbConnection)

	def parse(self, url):
		feed = feedparser.parse(url)
		if feed["bozo"]:
			level = "Warning" if feed["entries"] else "Error"
			print "Feed %s: %s (%s)" % (level, feed["bozo_exception"], url)
		return feed

	def stripHtml(self, htmlContent):
		return re.sub('<[^<]+?>', '', htmlContent)

	def github(self, token):
		private = ["https://github.com/organizations/hickerspace/basti2342.private.atom?token=%s" % token]

		for url in private:
			feed = self.parse(url)
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
			feed = self.parse(url)
			for entry in feed["entries"]:
				cleanContent = self.stripHtml(entry["content"][0]["value"])
				self.insert(entry["updated_parsed"], "Facebook", "Pinnwand", entry["link"], cleanContent)

	def youtube(self):
		urls = ["http://gdata.youtube.com/feeds/base/users/hickerspace/uploads?alt=rss&v=2&orderby=published"]
		service = "YouTube"
		for url in urls:
			# get videos
			feed = self.parse(url)
			for entry in feed["entries"]:
				self.insert(entry["updated_parsed"], service, "Video", entry["link"], entry["title"])

			# get comments
			for entry in feed["entries"]:
				id = re.findall(r"v=(.*)[&$]", entry["link"])[0]
				title = entry["title"]
				link = "http://www.youtube.com/all_comments?v=%s" % id

				commentFeed = self.parse("https://gdata.youtube.com/feeds/api/videos/%s/comments" % id)
				for commentEntry in commentFeed["entries"]:
					content = 'Kommentar zu "%s": %s' % (title, commentEntry["subtitle"]
						.encode("latin-1", "ignore"))
					self.insert(entry["updated_parsed"], service, "Kommentar", link, content)

	def wiki(self):
		urls = ["http://hickerspace.org/w/index.php?title=Spezial:Letzte_%C3%84nderungen&feed=atom"]

		for url in urls:
			feed = self.parse(url)
			for entry in feed["entries"]:
				# try to parse edit summary
				summaryMatch = re.findall(r"^<p>(.+?)</p>", entry["summary"])
				summary = ": %s" % self.stripHtml(summaryMatch[0]) if summaryMatch else ""
				content = "%s%s" % (entry["title"], summary)

				self.insert(entry["updated_parsed"], "Wiki", "Activity", entry["link"], \
					content.encode("latin-1", "ignore"), entry["author"])

	def soup(self, token):
		accountRss = "http://hickerspace.soup.io/rss"
		notifyRss = "http://www.soup.io/notifications/%s.rss" % token
		service = "Soup"

		feedAcc = self.parse(accountRss)
		for entry in feedAcc["entries"]:
			attributes = json.loads(entry["soup_attributes"])
			body = self.stripHtml(attributes["body"])
			link = entry["links"][-1]["href"]
			self.insert(entry["updated_parsed"], service, "Post", link, body.encode("latin-1", "ignore"))

		feedNotify = self.parse(notifyRss)
		for entry in feedNotify["entries"]:
			authorMatches = re.findall(r"<span class=\"name\">(.+?)</span>", entry["summary"])
			author = authorMatches[0] if authorMatches else ""
			self.insert(entry["updated_parsed"], service, "Notification", entry["link"], entry["title"].encode("latin-1", "ignore"), author)

