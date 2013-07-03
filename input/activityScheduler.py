#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apscheduler.scheduler import Scheduler
import baseRunner, time, logging

class ActivityScheduler(baseRunner.BaseRunner):
	def __init__(self):
		super(ActivityScheduler, self).__init__()

		conf = self.config._sections["logging"]
		del conf["__name__"]
		conf["level"] = int(conf["level"])
		logging.basicConfig(**conf)

		self.scheduler = Scheduler()
		self.scheduler.start()

		if not self.scheduler.get_jobs():
			self.createSchedule()

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
		del schedules["__name__"]
		for methodName, schedule in schedules.items():
			self.scheduler.add_cron_job(self.wrap, *schedule.split(), args=[methodName], misfire_grace_time=120)

if __name__ == '__main__':
	ActivityScheduler()
