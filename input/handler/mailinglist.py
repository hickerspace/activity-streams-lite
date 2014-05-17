#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, urllib, urllib2, locale, json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
from os.path import dirname, abspath, join
from os import sep
import logging

"""
MailinglistHandler provides a method that scrapes mailman archives and detects mails of current
and last month. Supports archives requiring authentication.
"""
class MailinglistHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(MailinglistHandler, self).__init__(dbConnection)
		self.subscriberFile = join(dirname(abspath(__file__)), \
			"..%(sep)sdata%(sep)ssubscribers.json" % {"sep": sep})
		self.service = "mailing-list"

	def mailman(self, **args):
		# call ALL the mailman methods
		self.do(self.posts, **args)
		self.do(self.subscribers, **args)

	def posts(self, weburl, listname, language, loginmail="", loginpassword=""):
		self.type_ = "new-mail"
		auth = urllib.urlencode({"username": loginmail, "password": loginpassword})
		# current and last month
		dates = [datetime.now(), datetime.now() - relativedelta(months=1)]
		for date in dates:
			# request archive index for specific month
			locale.setlocale(locale.LC_TIME, 'C')
			privateUrl = "%sprivate/%s/%d-%s/" % (weburl, listname, date.year, \
				date.strftime("%B"))
			locale.setlocale(locale.LC_TIME, '')

			idxUrl = "%sdate.html" % privateUrl
			request = urllib2.Request(idxUrl, auth)
			archiveIdx = urllib2.urlopen(request).read()
			parser = etree.HTMLParser()
			idxTree = etree.fromstring(archiveIdx, parser)
			# forms indicate login, so authentication failed
			if idxTree.xpath('//form'):
				print "Authentication for %s with %s failed." % (listname, loginmail)
				break

			mailLinks = idxTree.xpath('/html/body/ul[2]/li/a/@href')

			for mailLink in mailLinks:
				# fetch mail
				mailUrl = "%s%s" % (privateUrl, mailLink)
				request = urllib2.Request(mailUrl, auth)
				mail = urllib2.urlopen(request).read()
				mailTree = etree.fromstring(mail, parser)
				mailDate = mailTree.xpath('/html/body/i/text()')

				if mailDate:
					mailDate = mailDate[0].replace("  ", " ")
					try:
						mailDate = self.strToDatetime(mailDate, language)
					except ValueError:
						mailDate = self.strToDatetime(mailDate)

					self.insert(mailDate, mailUrl, "New mail on %s mailing list." \
						% listname.title())

	def strToDatetime(self, dateStr, language='C'):
		# convert string to datetime
		locale.setlocale(locale.LC_TIME, language)
		try:
			mailDate = datetime.strptime(dateStr.encode("utf-8"), "%a %b %d %H:%M:%S %Z %Y")
		except ValueError:
			self.logError("Did you set the correct mailinglist language?")
		locale.setlocale(locale.LC_TIME, '')
		return mailDate

	def subscribers(self, weburl, listname, language, loginmail="", loginpassword=""):
		self.type_ = "new-subscriber"
		post = urllib.urlencode({"roster-email": loginmail, "roster-pw": loginpassword})
		request = urllib2.Request("%sroster/%s" % (weburl, listname), post)
		subscribers = urllib2.urlopen(request).read()
		parser = etree.HTMLParser()
		subscriberTree = etree.fromstring(subscribers, parser)
		nonDigested = subscriberTree.xpath('/html/body/table/tr[3]/td/center/b/font/text()')[0].split()[0]
		digested = subscriberTree.xpath('/html/body/table/tr[3]/td[2]/center/b/font/text()')[0].split()[0]
		newSubscriberNum = int(nonDigested) + int(digested)

		try:
			with open(self.subscriberFile) as f:
				oldSubscriberNums = json.load(f)
				if newSubscriberNum > oldSubscriberNums[listname]:
					diff = newSubscriberNum - oldSubscriberNums[listname]
					content = "%d new subscribers" % diff if diff > 1 else "New subscriber"

					self.insert(datetime.now(), "%slistinfo/%s#subscribers" % (weburl, listname), \
						"%s on %s mailing list." % (content, listname.title()))
		except IOError:
			# file doesn't exist yet
			oldSubscriberNums = {}
		except KeyError:
			# no subscriber value for list found
			pass

		with open(self.subscriberFile, "w") as f:
			oldSubscriberNums[listname] = newSubscriberNum
			json.dump(oldSubscriberNums, f)

