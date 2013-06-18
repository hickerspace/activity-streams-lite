#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

"""
Simple global logging.
Import the logger like this:
	from logger import log
and use it like this:
	log.debug("This is a debug message.")
"""
logging.basicConfig(
	level=logging.INFO,
	filename='asl.log',
	format='%(asctime)s %(levelname)-8s %(message)s',
	datefmt='%d.%m.%Y %H:%M:%S')

log = logging.getLogger('asl')

