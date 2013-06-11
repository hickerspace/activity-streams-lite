#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apscheduler.scheduler import Scheduler
import baseRunner, time, logging

class ActivityScheduler(baseRunner.BaseRunner):
	def __init__(self):
		super(ActivityScheduler, self).__init__()
		logging.basicConfig(level=logging.DEBUG, filename="debug.log", format='%(asctime)s %(levelname)-8s %(message)s', datefmt="%d.%m.%Y %H:%M:%S")

		self.scheduler = Scheduler()
		self.scheduler.start()

		if not self.scheduler.get_jobs():
			self.createSchedule()

		logging.info("Initial tasks completed. Waiting for next event..")

		while True:
			try:
				time.sleep(10)
			except KeyboardInterrupt:
				logging.info("Shutting down..")
				self.scheduler.shutdown()
				quit()

	def createSchedule(self):
		logging.info("Schedule requests..")

		schedules = self.config._sections["schedule"]
		del schedules["__name__"]
		for method, schedule in schedules.items():
			self.scheduler.add_cron_job(self.wrap, *schedule.split(), args=[getattr(self, method)], misfire_grace_time=120)

if __name__ == '__main__':
	ActivityScheduler()
