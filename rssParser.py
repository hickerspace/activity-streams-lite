#!/usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser, re

def github():
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
			message = "[github] %s by %s: %s <%s>" % (feed["feed"]["title"], entry["author"], entry["title"], entry["link"])
			print message

def facebook():
	urls = ["http://www.facebook.com/feeds/page.php?format=atom10&id=148681465224497"]

	for url in urls:
		feed = feedparser.parse(url)
		for entry in feed["entries"]:
			# strip html
			cleanContent = re.sub('<[^<]+?>', '', entry["content"][0]["value"])
			message = "[Facebook] %s <%s>" % (cleanContent, entry["link"])
			print message

def youtube():
	urls = ["http://gdata.youtube.com/feeds/base/users/hickerspace/uploads?alt=rss&v=2&orderby=published"]

	for url in urls:
		# get videos
		feed = feedparser.parse(url)
		for entry in feed["entries"]:
			message = "[YouTube] Neues Video: %s <%s>" % (entry["title"], entry["link"])
			print message

		# get comments
		for entry in feed["entries"]:
			id = re.findall(r"v=(.*)[&$]", entry["link"])[0]
			title = entry["title"]
			link = "http://www.youtube.com/all_comments?v=%s" % id

			commentFeed = feedparser.parse("https://gdata.youtube.com/feeds/api/videos/%s/comments" % id)
			for commentEntry in commentFeed["entries"]:
				message = "[YouTube] Neuer Kommentar zu \"%s\": %s <%s>" % (title, commentEntry["summary"], link)
				print message

def main():
	print "GitHub:"
	github()

	print "Facebook:"
	facebook()

	print "YouTube:"
	youtube()

if  __name__ == "__main__":
	main()
