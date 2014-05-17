#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apscheduler.scheduler import Scheduler
import baseRunner, time, logging
from os.path import join, dirname

"""
The activity scheduler contains the main loop and creates the request schedule
as defined in the config.
"""
class ActivityScheduler(baseRunner.BaseRunner):
	def __init__(self):
		super(ActivityScheduler, self).__init__()

		# set logging options as defined in config file
		logConf = self.config._sections["logging"]
		# remove default __name__ item
		del logConf["__name__"]
		logConf["level"] = int(logConf["level"])
		logConf["filename"] = join(dirname(__file__), logConf["filename"])
		logging.basicConfig(**logConf)

		# initialize scheduler
		self.scheduler = Scheduler()
		self.scheduler.start()

		# create initial schedule
		if not self.scheduler.get_jobs():
			self.createSchedule()

		# main loop
		while True:
			try:
				time.sleep(10)
			except KeyboardInterrupt:
				logging.info("Shutting down..")
				self.scheduler.shutdown()
				break

	def createSchedule(self):
		logging.info("Schedule requests..")

		schedules = self.config._sections["schedule"]
		# remove default __name__ item
		del schedules["__name__"]
		for methodName, schedule in schedules.items():
			# schedule handler requests (wrapper method gets called with
			# cron-like notation and the method name)
			# name parameter is given for logging/debugging purposes only
			self.scheduler.add_cron_job(self.wrap, *schedule.split(), \
				args=[methodName], misfire_grace_time=120, name=methodName)

if __name__ == '__main__':
	ActivityScheduler()
