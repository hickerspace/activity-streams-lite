#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, feedparser, re, json
from lxml import etree

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

	def githubOrga(self, orga, user, token):
		url = "https://github.com/organizations/%s/%s.private.atom?token=%s" \
			% (orga, user, token)

		feed = self.parse(url)
		for entry in feed["entries"]:
			type = "activity"
			# try to get the specific event from the id
			typeMatch = re.findall(r"^tag:github.com,2008:(.*?)Event/\d+$", entry["id"])
			if typeMatch:
				type = typeMatch[0].lower()
				# try to add *what* got created
				try:
					createTypes = ["repository", "branch"]
					createType = entry["title"].split()[2].lower()
					if type == "create" and createType in createTypes:
						type += " %s" % createType
				except IndexError:
					print "Could not extract extended create information."
			# get summary
			parser = etree.HTMLParser()
			tree = etree.fromstring(entry["content"][0]["value"], parser)
			summaries = tree.xpath("//blockquote/text()")
			summary = "; ".join([ s.strip(" \n") for s in summaries ])
			content = "%s: %s" % (entry["title"], summary) if summary else entry["title"]

			self.insert(entry["updated_parsed"], "github", type, entry["link"],	content, \
				entry["author"])

	def facebook(self, id):
		url = "http://www.facebook.com/feeds/page.php?format=atom10&id=%s" % id

		feed = self.parse(url)
		for entry in feed["entries"]:
			cleanContent = self.stripHtml(entry["content"][0]["value"])
			self.insert(entry["updated_parsed"], "facebook", "wall", \
				entry["link"], cleanContent)

	def youtube(self, user):
		url = "http://gdata.youtube.com/feeds/base/users/%s/uploads" % user \
			+ "?alt=rss&v=2&orderby=published"
		service = "youtube"

		# get videos
		feed = self.parse(url)
		for entry in feed["entries"]:
			self.insert(entry["updated_parsed"], service, "video", \
				entry["link"], entry["title"])

		# get comments
		for entry in feed["entries"]:
			id = re.findall(r"v=(.*)[&$]", entry["link"])[0]
			title = entry["title"]
			link = "http://www.youtube.com/all_comments?v=%s" % id

			commentFeed = self.parse("https://gdata.youtube.com/feeds/api/videos/%s/comments" \
				% id)
			for commentEntry in commentFeed["entries"]:
				content = 'Comment on "%s": %s' % (title, commentEntry["subtitle"] \
					.encode("latin-1", "ignore"))
				self.insert(entry["updated_parsed"], service, "comment", link, content)

	def mediaWiki(self, url):
		feed = self.parse(url)
		for entry in feed["entries"]:
			# try to parse edit summary
			summaryMatch = re.findall(r"^<p>(.+?)</p>", entry["summary"])
			summary = ": %s" % self.stripHtml(summaryMatch[0]) if summaryMatch else ""
			content = "%s%s" % (entry["title"], summary)

			self.insert(entry["updated_parsed"], "wiki", "activity", entry["link"], \
				content.encode("latin-1", "ignore"), entry["author"])

	def soup(self, user, token):
		accountRss = "http://%s.soup.io/rss" % user
		notifyRss = "http://www.soup.io/notifications/%s.rss" % token
		service = "soup"

		feedAcc = self.parse(accountRss)
		for entry in feedAcc["entries"]:
			attributes = json.loads(entry["soup_attributes"])
			body = self.stripHtml(attributes["body"])
			link = entry["links"][-1]["href"]
			self.insert(entry["updated_parsed"], service, "post", link, \
				body.encode("latin-1", "ignore"))

		feedNotify = self.parse(notifyRss)
		for entry in feedNotify["entries"]:
			# skip maintenance messages
			if entry["link"][:22] == "http://updates.soup.io": continue
			authorMatches = re.findall(r"<span class=\"name\">(.+?)</span>", entry["summary"])
			author = authorMatches[0] if authorMatches else ""
			self.insert(entry["updated_parsed"], service, "notification", entry["link"], \
				entry["title"].encode("latin-1", "ignore"), author)

