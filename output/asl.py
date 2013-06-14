#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from flask import Flask, request, render_template, g, jsonify
from werkzeug.contrib.atom import AtomFeed
from logger import log

DEBUG = True
ORGANZIZATION = ''

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

@app.route('/')
def welcome():
	g.cursor.execute('SELECT DISTINCT service, type FROM `activities`')
	entries = {}
	for row in g.cursor.fetchall():
		if row[0] not in entries: entries[row[0]] = []
		entries[row[0]].append(row[1])
	return render_template('show_entries.html', entries=entries)

@app.route('/asl.json')
def jsonOutput():
	#request.args.get('myParam')
	g.cursor.execute('SELECT datetime, person, service, type, content, url FROM `activities`' \
		+ ' ORDER BY `datetime` DESC LIMIT 30')
	entries = [dict(datetime=str(row[0]), person=row[1], \
		service=row[2], type=row[3], content=row[4], url=row[5]) \
		for row in g.cursor.fetchall()]
	return jsonify(results=entries)

@app.route('/asl.atom')
def atomOutput():
	g.cursor.execute('SELECT datetime, person, service, type, content, url FROM `activities`' \
		+ ' ORDER BY `datetime` DESC LIMIT 30')

	feed = AtomFeed('%s - Activity Streams Lite' % app.config['ORGANIZATION'], \
		feed_url=request.url, url=request.url_root, subtitle='Syndicating %s activities' \
		% app.config['ORGANIZATION'])

	for row in g.cursor.fetchall():
		datetime, person, service, type, content, url = row
		categories = [dict(term=service, label="service"), dict(term=type, label="type")]
		title = '%s..' % content[:50] if len(content) > 52 else content
		feed.add(unicode(title), unicode(content), content_type='text', \
			author=person, url=url, updated=datetime, categories=categories)

	return feed.get_response()

