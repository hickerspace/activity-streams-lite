#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, feedparser, re, json, socket
from lxml import etree

"""
FeedHandler parses feeds and inserts particular parts into the database.
"""
class FeedHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(FeedHandler, self).__init__(dbConnection)
		# sometimes feeds are slow, so be patient
		socket.setdefaulttimeout(10)

	def parse(self, url):
		feed = feedparser.parse(url)
		# feed parsing successfull?
		if feed["bozo"]:
			level = "Warning" if feed["entries"] else "Error"
			self.log("Feed %s: %s (%s)" % (level, feed["bozo_exception"], url))
		return feed

	def stripHtml(self, htmlContent):
		# get rid of HTML code
		return re.sub('<[^<]+?>', '', htmlContent)

	def github(self, organization, user, token):
		self.service = "github"
		url = "https://github.com/organizations/%s/%s.private.atom?token=%s" \
			% (organization, user, token)

		feed = self.parse(url)
		for entry in feed["entries"]:
			self.type_ = "activity"
			# try to get the specific event from the id
			typeMatch = re.findall(r"^tag:github.com,2008:(.*?)Event/\d+$", entry["id"])
			if typeMatch and typeMatch[0]:
				self.type_ = typeMatch[0].lower()
				# try to add *what* got created
				try:
					createTypes = ["repository", "branch"]
					createType = entry["title"].split()[2].lower()
					if self.type_ == "create" and createType in createTypes:
						self.type_ += "-%s" % createType
				except IndexError as e:
					self.log("Could not extract extended create information.")
			# get summary
			parser = etree.HTMLParser()
			tree = etree.fromstring(entry["content"][0]["value"], parser)
			summaries = tree.xpath("//blockquote/text()")
			summary = "; ".join([ s.strip(" \n") for s in summaries ])
			content = "%s: %s" % (entry["title"], summary) if summary else entry["title"]

			self.insert(entry["updated_parsed"], entry["link"],	content, \
				entry["author"])
			self.updateStats(allTypes=True)

	def facebook(self, id):
		self.service = "facebook"
		self.type_ = "wall"
		url = "http://www.facebook.com/feeds/page.php?format=atom10&id=%s" % id

		feed = self.parse(url)
		for entry in feed["entries"]:
			cleanContent = self.stripHtml(entry["content"][0]["value"])
			self.insert(entry["updated_parsed"], entry["link"], cleanContent)

	def youtube(self, user):
		url = "http://gdata.youtube.com/feeds/base/users/%s/uploads" % user \
			+ "?alt=rss&v=2&orderby=published"
		self.service = "youtube"

		# get videos
		self.type_ = "video"
		feed = self.parse(url)
		for entry in feed["entries"]:
			self.insert(entry["updated_parsed"], entry["link"], entry["title"])

		# update manually because posts *and* notifications get checked here
		self.updateStats()

		# get comments
		self.type_ = "comment"
		for entry in feed["entries"]:
			id = re.findall(r"v=(.*)[&$]", entry["link"])[0]
			title = entry["title"]
			link = "http://www.youtube.com/all_comments?v=%s" % id

			commentFeed = self.parse("https://gdata.youtube.com/feeds/api/videos/%s/comments" \
				% id)
			for commentEntry in commentFeed["entries"]:
				content = 'Comment on "%s": %s' % (title, commentEntry["subtitle"])
				author = commentEntry["author"]
				self.insert(entry["updated_parsed"], link, content, author)

	def mediawiki(self, feedurl):
		self.service = "wiki"
		self.type_ = "activity"
		feed = self.parse(feedurl)
		for entry in feed["entries"]:
			# try to parse edit summary
			summaryMatch = re.findall(r"^<p>(.+?)</p>", entry["summary"])
			summary = ": %s" % self.stripHtml(summaryMatch[0]) if summaryMatch else ""
			content = "%s%s" % (entry["title"], summary)

			self.insert(entry["updated_parsed"], entry["link"], \
				content, entry["author"])

	def soup(self, user, token):
		accountRss = "http://%s.soup.io/rss" % user
		notifyRss = "http://www.soup.io/notifications/%s.rss" % token
		self.service = "soup"

		self.type_ = "post"
		feedAcc = self.parse(accountRss)
		for entry in feedAcc["entries"]:
			attributes = json.loads(entry["soup_attributes"])
			body = self.stripHtml(attributes["body"])
			link = entry["links"][-1]["href"]
			self.insert(entry["updated_parsed"], link, body)

		# update manually because posts *and* notifications get checked here
		self.updateStats()

		self.type_ = "notification"
		feedNotify = self.parse(notifyRss)
		for entry in feedNotify["entries"]:
			# skip maintenance messages
			if entry["link"][:22] == "http://updates.soup.io": continue
			authorMatches = re.findall(r"<span class=\"name\">(.+?)</span>", entry["summary"])
			author = authorMatches[0] if authorMatches else ""
			self.insert(entry["updated_parsed"], entry["link"], entry["title"], author)

