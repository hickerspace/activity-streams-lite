#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from flask import Flask, request, render_template, g, jsonify
from werkzeug.contrib.atom import AtomFeed
from logger import log

ORGANIZATION = ''
SERVICES = {'wiki': ['activity'],
			'github': ['push', 'create-repository', 'create-branch', 'fork', 'watch', 'member', \
				'follow'],
			'mailing-list': ['new-mail', 'new-subscriber'],
			'twitter': ['tweet', 'retweet', 'reply', 'mention'],
			'youtube': ['video', 'comment'],
			'soup': ['post', 'notification'],
			'facebook': ['wall'],
			'sensor': ['mate-o-meter', 'traffic-light', 'room']}

# database
HOST = ''
DATABASE = ''
USER = ''
PASSWORD = ''

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(__name__)

@app.before_request
def before_request():
	g.db = MySQLdb.connect(app.config['HOST'], app.config['USER'], app.config['PASSWORD'], \
		 app.config['DATABASE'], charset="utf8", use_unicode=True)
	g.cursor = g.db.cursor()

@app.teardown_request
def teardown_request(exception):
	# close cursor
	cursor = getattr(g, 'cursor', None)
	if not cursor:
		cursor.close()

	# close db
	db = getattr(g, 'db', None)
	if not db:
		db.close

def getActivities():
	# pagination
	try:
		page = int(request.args['page'])
		if page < 1: raise KeyError
	except (KeyError, ValueError):
		page = 1

	# save point (last_id)
	wheres = []
	try:
		wheres.append('pk_id > %d' % int(request.args['last_id']))
	except (KeyError, ValueError):
		# no or invalid last_id
		pass

	# filter (select/deselect)
	selected = []
	deselected = []
	for arg in request.args:
		try:
			count = arg.count(".")
			# incomplete filter
			if count == 1:
				service, type_ = arg.split(".")
				account = "*"
			else:
				service, type_, account = arg.split(".")

			# remove %
			service, type_, account = [ x.replace("%", "") for x in (service, type_, account) ]

			# accept only * as wildcards
			if type_ == '*': type_ = '%'
			if account == '*': account = '%'

			if service[0] == "-": deselected += [service[1:], type_, account]
			else: selected += [service, type_, account]
		except ValueError:
			continue

	# build "select service/type" prepared statement
	prepSelect = ['(service LIKE %s AND type LIKE %s AND account LIKE %s)']*(len(selected)/3)
	deselect = ['NOT (service LIKE %s AND type LIKE %s AND account LIKE %s)']*(len(deselected)/3)

	if prepSelect: wheres.append(' OR '.join(prepSelect))
	if deselect: wheres.append(' AND '.join(deselect))

	# build WHERE
	where = ' WHERE %s' % ' AND '.join(wheres) if wheres else ""
	g.cursor.execute('SELECT pk_id, datetime, person, service, type, account, content, url FROM `activities`' \
		+ '%s ORDER BY `datetime` DESC LIMIT %d,%d' % (where, (page-1)*30, (page)*30), selected+deselected)
	return g.cursor.fetchall()

@app.route('/')
def welcome():
	g.cursor.execute('SELECT DISTINCT service, account FROM `activities`')
	accounts = { }
	for (s, a) in g.cursor.fetchall():
		if s in accounts:
			accounts[s].append(a)
		else:
			accounts[s] = [a]
	return render_template('show_entries.html', entries=app.config['SERVICES'], accounts=accounts)

@app.route('/asl.json')
def jsonOutput():
	entries = [dict(id=row[0], datetime=str(row[1]), person=row[2], \
		service=row[3], type=row[4], account=row[5], content=row[6], url=row[7]) \
		for row in getActivities()]
	return jsonify(results=entries)

@app.route('/asl.atom')
def atomOutput():
	feed = AtomFeed('%s - Activity Streams Lite' % app.config['ORGANIZATION'], \
		feed_url=request.url, url=request.url_root, subtitle='Syndicating %s activities' \
		% app.config['ORGANIZATION'])

	for row in getActivities():
		id, datetime, person, service, type, account, content, url = row
		categories = [dict(term=service, label="service"), dict(term=type, label="type")]
		title = '[%s] @%s %s' % (service, account, type)
		feed.add(unicode(title), unicode(content), content_type='text', \
			author=person, url=url, updated=datetime, categories=categories, id=id)

	return feed.get_response()

