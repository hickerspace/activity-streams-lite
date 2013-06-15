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
			'mailing-list': ['kontakt', 'hickerspace'],
			'twitter': ['tweet', 'reply', 'mention'],
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
	# generate (service, type)-tuples
	combos = [(service, type) for service, types in app.config['SERVICES'].items() \
		for type in types]
	# which service-type-combinations got requested?
	reqServices = [r for row in combos if ".".join(row) in request.args for r in row]
	# build prepared statement
	where = 'WHERE %s' % ' OR '.join(['(service = %s and type = %s)'] * (len(reqServices)/2)) \
		if reqServices else ""
	g.cursor.execute('SELECT datetime, person, service, type, content, url FROM `activities`' \
		+ '%s ORDER BY `datetime` DESC LIMIT 30' % where, reqServices)
	return g.cursor.fetchall()

@app.route('/')
def welcome():
	return render_template('show_entries.html', entries=app.config['SERVICES'])

@app.route('/asl.json')
def jsonOutput():
	entries = [dict(datetime=str(row[0]), person=row[1], \
		service=row[2], type=row[3], content=row[4], url=row[5]) \
		for row in getActivities()]
	return jsonify(results=entries)

@app.route('/asl.atom')
def atomOutput():
	feed = AtomFeed('%s - Activity Streams Lite' % app.config['ORGANIZATION'], \
		feed_url=request.url, url=request.url_root, subtitle='Syndicating %s activities' \
		% app.config['ORGANIZATION'])

	for row in getActivities():
		datetime, person, service, type, content, url = row
		categories = [dict(term=service, label="service"), dict(term=type, label="type")]
		title = '%s..' % content[:50] if len(content) > 52 else content
		feed.add(unicode(title), unicode(content), content_type='text', \
			author=person, url=url, updated=datetime, categories=categories)

	return feed.get_response()

