#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base, urllib, urllib2
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

"""
MailinglistHandler provides a method that scrapes mailman archives and detects mails of current
and last month. Supports archives requiring authentication.
"""
class MailinglistHandler(base.BaseHandler):
	def __init__(self, dbConnection):
		super(MailinglistHandler, self).__init__(dbConnection)

	def posts(self, mailmanUrl, listName, mail="", password=""):
		auth = urllib.urlencode({"username": mail, "password": password})
		# current and last month
		dates = [datetime.now(), datetime.now() - relativedelta(months=1)]
		for date in dates:
			# request archive index for specific month
			privateUrl = "%sprivate/%s/%d-%s/" % (mailmanUrl, listName, date.year, \
				date.strftime("%B"))
			idxUrl = "%sdate.html" % privateUrl
			request = urllib2.Request(idxUrl, auth)
			archiveIdx = urllib2.urlopen(request).read().decode('utf-8')
			parser = etree.HTMLParser()
			idxTree = etree.fromstring(archiveIdx, parser)
			# forms indicate login, so authentication failed
			if idxTree.xpath('//form'):
				print "Authentication for %s with %s failed." % (listName, mail)
				break

			mailLinks = idxTree.xpath('/html/body/ul[2]/li/a/@href')

			for mailLink in mailLinks:
				# fetch mail
				mailUrl = "%s%s" % (privateUrl, mailLink)
				request = urllib2.Request(mailUrl, auth)
				mail = urllib2.urlopen(request).read().decode('utf-8')
				mailTree = etree.fromstring(mail, parser)
				mailDate = mailTree.xpath('/html/body/i/text()')

				if mailDate:
					# convert string to datetime
					mailDate = datetime.strptime(mailDate[0], "%a %b  %d %H:%M:%S %Z %Y")

					self.insert(mailDate, "Mailingliste", listName.title(), mailUrl, \
						"Neue Mail auf der %s-Mailingliste." % listName.title())

