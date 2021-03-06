Activity Streams Lite
=====================

Syndicating Hickerspace activities from different sources like GitHub, YouTube, Facebook and many more.
This project is based on the idea of [Activity Streams](http://activitystrea.ms/).

Configure db access, private tokens and other credentials in `config`. See `config.sample` for inspiration.

Execute `activityScheduler.py` to start.

## Dependencies input
* MySQLdb
* APScheduler
* feedparser
* lxml
* dateutil
* tweepy
* httplib2

`pip install MySQL-python apscheduler feedparser lxml python-dateutil tweepy httplib2`

## Dependencies output
* Flask
* MySQLdb

`pip install MySQL-python Flask`

## How will it work?
See our nice [chart](http://hickerspace.org/wiki/Datei:Activitystreams.jpg).

## Demo
Try a live demo at http://asl.hickerspace.org.

## Input
### To be done
* Web form
* Sound/LEDTicker (?)

### Done
* Feeds
  * GitHub
  * YouTube
  * Facebook
  * Wiki
  * Soup
* Hickerspace API
  * Room status
  * Mate-O-Meter
  * Traffic light
* Twitter (timeline + mentions via Twitter-API)
* Mailing lists (posts + new subscribers)

## Output
* JSON/Atom output
* Filter added (append (multiple) service.type as GET parameters)
* Pagination & Save Point (last_id) added
* wildcards introduced

## Known bugs
* datetime is currently local, but the atom feed generator thinks that it's UTC.
