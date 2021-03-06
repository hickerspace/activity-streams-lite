#!/usr/bin/python
# -*- coding: utf-8 -*-

import base, tweepy, re, httplib2, json
from os import sep
from os.path import dirname, abspath, join
from dateutil import tz

class TwitterHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(TwitterHandler, self).__init__(dbConnection)

		self.service = "twitter"
		# cache expanded urls in file
		self.expandedUrls = join(dirname(abspath(__file__)), \
			"..%(sep)sdata%(sep)sexpanded_urls.json" % {"sep": sep})

	def twitter(self, **args):
		try:
			# call ALL the twitter methods
			self.auth(**args)
			self.do(self.timeline)
			self.do(self.mentions)
		except Exception as e:
			# auth failed (other exceptions get caught by self.do() )
			self.logError(e)

	def auth(self, consumerkey, consumersecret, accesstoken, accesstokensecret):
		# create Twitter connection
		auth = tweepy.OAuthHandler(consumerkey, consumersecret)
		auth.set_access_token(accesstoken, accesstokensecret)
		self.api = tweepy.API(auth)

	def resolve(self, url, expanded):
		# resolve redirections
		h = httplib2.Http()
		h.follow_redirects = False

		try:
			target = h.request(url, 'HEAD')[0]['location']
		except (KeyError, httplib2.SSLHandshakeError, UnicodeError):
			# meh, borken SSL or borken unicode, use short link
			target = url

		with open(self.expandedUrls, 'w') as f:
			expanded[url] = target
			json.dump(expanded, f)

		return target

	def expand(self, text, lastRun=False):
		# expands short links, because nobody likes t.co
		if not lastRun:
			text = self.expand(text, True)

		# try to find URLs - http://daringfireball.net/2010/07/improved_regex_for_matching_urls
		urlMatch = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
		matches = urlMatch.findall(text)
		matches = map(lambda match: match[0], matches)

		try:
			# load cached expanded URLs
			with open(self.expandedUrls, 'r') as f:
				expanded = json.load(f)
		except IOError:
			expanded = { }

		for url in matches:
			replacement = expanded[url] if url in expanded else self.resolve(url, expanded)
			text = text.replace(url, replacement)

		return text

	def insertStatus(self, status):
		# insert Twitter statuses

		# determine type of tweet
		if not self.type_ or self.type_ != "mention":
			if status.text[0] == "@":
				self.type_ = "reply"
			elif status.text[:3] == "RT ":
				self.type_ = "retweet"
			else:
				self.type_ = "tweet"

		try:
			author = status.author.screen_name
		except AttributeError:
			author = status.from_user

		url = "http://twitter.com/%s/statuses/%s" % (author, status.id_str)
		content = self.expand(status.text)

		source = "" if status.source == "web" else status.source
		person = author if self.type_ == "mention" else source

		# convert UTC datetime to local datetime
		date = status.created_at.replace(tzinfo=tz.tzutc())
		localDate = date.astimezone(tz.tzlocal())

		self.insert(localDate, url, content, person)

	def timeline(self):
		# let insertStatus() decide which type
		self.type_ = "tweet"
		for status in self.api.user_timeline(self.account):
			self.insertStatus(status)
		self.updateStats(allTypes=True)

	def mentions(self):
		self.type_ = "mention"
		withQuery = []
		withoutQuery = []
		# iterate through screen names
		for screenName in self.accounts:
			withQuery.append("@%s" % screenName)
			withQuery.append(screenName)
			withoutQuery.append("-from:%s" % screenName)

		query = "%s %s" % (" OR ".join(withQuery), " ".join(withoutQuery))

		results = tweepy.Cursor(self.api.search, q=query).items()
		for status in results:
			self.insertStatus(status)

		for status in tweepy.Cursor(self.api.mentions_timeline).items():
			self.insertStatus(status)
