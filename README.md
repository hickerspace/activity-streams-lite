Activity Streams Lite
=====================

Syndicating Hickerspace activities from different sources like GitHub, YouTube, Facebook and many more.
This project is based on the idea of [Activity Streams](http://activitystrea.ms/).

Configure db access, private tokens and other credentials in `config`.

Execute `activityScheduler.py` to start.

## Dependencies
* MySQLdb
* APScheduler
* feedparser
* lxml
* dateutil
* tweepy
* httplib2

`pip install MySQL-python apscheduler feedparser lxml python-dateutil tweepy httplib2`

## How will it work?
See our nice [chart](http://hickerspace.org/wiki/Datei:Activitystreams.jpg).

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
* Mailing lists

## Output
Nothing done yet.
