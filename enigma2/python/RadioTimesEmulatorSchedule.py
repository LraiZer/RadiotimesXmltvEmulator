from __future__ import print_function
from __future__ import absolute_import
from Components.config import config, configfile

from Screens.MessageBox import MessageBox

from enigma import eTimer

from .RadioTimesEmulator import RadioTimesEmulator

from time import localtime, time, strftime, mktime

autoScheduleTimer = None


def Scheduleautostart(reason, session=None, **kwargs):
	#
	# This gets called twice at start up,once by WHERE_AUTOSTART without session,
	# and once by WHERE_SESSIONSTART with session. WHERE_AUTOSTART is needed though
	# as it is used to wake from deep standby. We need to read from session so if
	# session is not set just return and wait for the second call to this function.
	#
	# Called with reason=1 during /sbin/shutdown.sysvinit, and with reason=0 at startup.
	# Called with reason=1 only happens when using WHERE_AUTOSTART.
	# If only using WHERE_SESSIONSTART there is no call to this function on shutdown.
	#
	print("[RadioTimesEmulator][Scheduleautostart] reason(%d), session" % reason, session)
	if reason == 0 and session is None:
		return
	global autoScheduleTimer
	global wasScheduleTimerWakeup
	wasScheduleTimerWakeup = False
	now = int(time())
	if reason == 0:
		if config.plugins.RadioTimesEmulator.schedule.value:
			# check if box was woken up by a timer, if so, check if this plugin set this timer. This is not conclusive.
			if session.nav.wasTimerWakeup() and abs(config.plugins.RadioTimesEmulator.nextscheduletime.value - time()) <= 360:
				wasScheduleTimerWakeup = True
				# if box is not in standby do it now
				from Screens.Standby import Standby, inStandby
				if not inStandby:
					# hack alert: session requires "pipshown" to avoid a crash in standby.py
					if not hasattr(session, "pipshown"):
						session.pipshown = False
					from Tools import Notifications
					Notifications.AddNotificationWithID("Standby", Standby)

		print("[RadioTimesEmulator][Scheduleautostart] AutoStart Enabled")
		if autoScheduleTimer is None:
			autoScheduleTimer = AutoScheduleTimer(session)
	else:
		print("[RadioTimesEmulator][Scheduleautostart] Stop")
		if autoScheduleTimer is not None:
			autoScheduleTimer.schedulestop()


class AutoScheduleTimer:
	instance = None
	def __init__(self, session):
		self.schedulename = "RadioTimesEmulator"
		self.config = config.plugins.RadioTimesEmulator
		self.itemtorun = RadioTimesEmulator
		self.session = session
		self.scheduletimer = eTimer()
		self.scheduletimer.callback.append(self.ScheduleonTimer)
		self.scheduleactivityTimer = eTimer()
		self.scheduleactivityTimer.timeout.get().append(self.scheduledatedelay)
		self.ScheduleTime = 0
		now = int(time())
		if self.config.schedule.value:
			print("[%s][AutoScheduleTimer] Schedule Enabled at " % self.schedulename, strftime("%c", localtime(now)))
			if now > 1546300800: # Tuesday, January 1, 2019 12:00:00 AM
				self.scheduledate()
			else:
				print("[%s][AutoScheduleTimer] STB clock not yet set." % self.schedulename)
				self.scheduleactivityTimer.start(36000)
		else:
			print("[%s][AutoScheduleTimer] Schedule Disabled at" % self.schedulename, strftime("%c", localtime(now)))
			self.scheduleactivityTimer.stop()

		assert AutoScheduleTimer.instance is None, "class AutoScheduleTimer is a singleton class and just one instance of this class is allowed!"
		AutoScheduleTimer.instance = self

	def __onClose(self):
		AutoScheduleTimer.instance = None

	def scheduledatedelay(self):
		self.scheduleactivityTimer.stop()
		self.scheduledate()

	def getScheduleTime(self):
		now = localtime(time())
		return int(mktime((now.tm_year, now.tm_mon, now.tm_mday, self.config.scheduletime.value[0], self.config.scheduletime.value[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))

	def getScheduleDayOfWeek(self):
		today = self.getToday()
		for i in range(1, 8):
			if self.config.days[(today+i)%7].value:
				return i

	def getToday(self):
		return localtime(time()).tm_wday

	def scheduledate(self, atLeast=0):
		self.scheduletimer.stop()
		self.ScheduleTime = self.getScheduleTime()
		now = int(time())
		if self.ScheduleTime > 0:
			if self.ScheduleTime < now + atLeast:
				self.ScheduleTime += 86400*self.getScheduleDayOfWeek()
			elif not self.config.days[self.getToday()].value:
				self.ScheduleTime += 86400*self.getScheduleDayOfWeek()
			next = self.ScheduleTime - now
			self.scheduletimer.startLongTimer(next)
		else:
			self.ScheduleTime = -1
		print("[%s][scheduledate] Time set to" % self.schedulename, strftime("%c", localtime(self.ScheduleTime)), strftime("(now=%c)", localtime(now)))
		self.config.nextscheduletime.value = self.ScheduleTime
		self.config.nextscheduletime.save()
		configfile.save()
		return self.ScheduleTime

	def schedulestop(self):
		self.scheduletimer.stop()

	def ScheduleonTimer(self):
		self.scheduletimer.stop()
		now = int(time())
		wake = self.getScheduleTime()
		atLeast = 0
		if wake - now < 60:
			atLeast = 60
			print("[%s][ScheduleonTimer] onTimer occured at" % self.schedulename, strftime("%c", localtime(now)))
			from Screens.Standby import inStandby
			if not inStandby:
				message = _("%s update is about to start.\nDo you want to allow this?") % self.schedulename
				ybox = self.session.openWithCallback(self.doSchedule, MessageBox, message, MessageBox.TYPE_YESNO, timeout=30)
				ybox.setTitle(_('%s scheduled update') % self.schedulename)
			else:
				self.doSchedule(True)
		self.scheduledate(atLeast)

	def doSchedule(self, answer):
		now = int(time())
		if answer is False:
			if self.config.retrycount.value < 2:
				print("[%s][doSchedule] Schedule delayed." % self.schedulename)
				self.config.retrycount.value += 1
				self.ScheduleTime = now + (int(self.config.retry.value) * 60)
				print("[%s][doSchedule] Time now set to" % self.schedulename, strftime("%c", localtime(self.ScheduleTime)), strftime("(now=%c)", localtime(now)))
				self.scheduletimer.startLongTimer(int(self.config.retry.value) * 60)
			else:
				atLeast = 60
				print("[%s][doSchedule] Enough Retries, delaying till next schedule." % self.schedulename, strftime("%c", localtime(now)))
				self.session.open(MessageBox, _("Enough Retries, delaying till next schedule."), MessageBox.TYPE_INFO, timeout=10)
				self.config.retrycount.value = 0
				self.scheduledate(atLeast)
		else:
			self.timer = eTimer()
			self.timer.callback.append(self.runscheduleditem)
			print("[%s][doSchedule] Running Schedule" % self.schedulename, strftime("%c", localtime(now)))
			self.timer.start(100, 1)

	def runscheduleditem(self):
		self.session.openWithCallback(self.runscheduleditemCallback, self.itemtorun)

	def runscheduleditemCallback(self):
		from Screens.Standby import Standby, inStandby, TryQuitMainloop, inTryQuitMainloop
		print("[%s][runscheduleditemCallback] inStandby" % self.schedulename, inStandby)
		if self.config.schedule.value and wasScheduleTimerWakeup and inStandby and self.config.scheduleshutdown.value and not self.session.nav.getRecordings() and not inTryQuitMainloop:
			print("[%s] Returning to deep standby after scheduled wakeup" % self.schedulename)
			self.session.open(TryQuitMainloop, 1)

	def doneConfiguring(self): # called from plugin on save
		now = int(time())
		if self.config.schedule.value:
			if autoScheduleTimer is not None:
				print("[%s][doneConfiguring] Schedule Enabled at" % self.schedulename, strftime("%c", localtime(now)))
				autoScheduleTimer.scheduledate()
		else:
			if autoScheduleTimer is not None:
				self.ScheduleTime = 0
				print("[%s][doneConfiguring] Schedule Disabled at" % self.schedulename, strftime("%c", localtime(now)))
				autoScheduleTimer.schedulestop()
		# scheduletext is not used for anything but could be returned to the calling function to display in the GUI.
		if self.ScheduleTime > 0:
			t = localtime(self.ScheduleTime)
			scheduletext = strftime(_("%a %e %b  %-H:%M"), t)
		else:
			scheduletext = ""
		return scheduletext

