from Components.config import config

from Screens.MessageBox import MessageBox
from Screens.Standby import inStandby

from enigma import eTimer

from RadioTimesEmulator import RadioTimesEmulator

from time import localtime, time, strftime, mktime

autoScheduleTimer = None
def Scheduleautostart(reason, session=None, **kwargs):
	"called with reason=1 to during /sbin/shutdown.sysvinit, with reason=0 at startup?"
	global autoScheduleTimer
	global _session
	now = int(time())
	if reason == 0:
		print "[RadioTimesEmulator][Scheduleautostart] AutoStart Enabled"
		if session is not None:
			_session = session
			if autoScheduleTimer is None:
				autoScheduleTimer = AutoScheduleTimer(session)
	else:
		print "[RadioTimesEmulator][Scheduleautostart] Stop"
		autoScheduleTimer.stop()

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
		now = int(time())
		global ScheduleTime
		if self.config.schedule.value:
			print "[%s][AutoScheduleTimer] Schedule Enabled at " % self.schedulename, strftime("%c", localtime(now))
			if now > 1262304000:
				self.scheduledate()
			else:
				print "[%s][AutoScheduleTimer] Time not yet set." % self.schedulename
				ScheduleTime = 0
				self.scheduleactivityTimer.start(36000)
		else:
			ScheduleTime = 0
			print "[%s][AutoScheduleTimer] Schedule Disabled at" % self.schedulename, strftime("%c", localtime(now))
			self.scheduleactivityTimer.stop()

		assert AutoScheduleTimer.instance is None, "class AutoScheduleTimer is a singleton class and just one instance of this class is allowed!"
		AutoScheduleTimer.instance = self

	def __onClose(self):
		AutoScheduleTimer.instance = None

	def scheduledatedelay(self):
		self.scheduleactivityTimer.stop()
		self.scheduledate()

	def getScheduleTime(self):
		backupclock = self.config.scheduletime.value
		nowt = time()
		now = localtime(nowt)
		return int(mktime((now.tm_year, now.tm_mon, now.tm_mday, backupclock[0], backupclock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))

	def scheduledate(self, atLeast = 0):
		self.scheduletimer.stop()
		global ScheduleTime
		ScheduleTime = self.getScheduleTime()
		now = int(time())
		if ScheduleTime > 0:
			if ScheduleTime < now + atLeast:
				if self.config.repeattype.value == "daily":
					ScheduleTime += 24*3600
					while (int(ScheduleTime)-30) < now:
						ScheduleTime += 24*3600
				elif self.config.repeattype.value == "every 3 days":
					ScheduleTime += 3*24*3600
					while (int(ScheduleTime)-30) < now:
						ScheduleTime += 3*24*3600
				elif self.config.repeattype.value == "weekly":
					ScheduleTime += 7*24*3600
					while (int(ScheduleTime)-30) < now:
						ScheduleTime += 7*24*3600
#				elif self.config.repeattype.value == "monthly":
#					ScheduleTime += 30*24*3600
#					while (int(ScheduleTime)-30) < now:
#						ScheduleTime += 30*24*3600
			next = ScheduleTime - now
			self.scheduletimer.startLongTimer(next)
		else:
			ScheduleTime = -1
		print "[%s][scheduledate] Time set to" % self.schedulename, strftime("%c", localtime(ScheduleTime)), strftime("(now=%c)", localtime(now))
		return ScheduleTime

	def backupstop(self):
		self.scheduletimer.stop()

	def ScheduleonTimer(self):
		self.scheduletimer.stop()
		now = int(time())
		wake = self.getScheduleTime()
		# If we're close enough, we're okay...
		atLeast = 0
		if wake - now < 60:
			atLeast = 60
			print "[%s][ScheduleonTimer] onTimer occured at" % self.schedulename, strftime("%c", localtime(now))
			from Screens.Standby import inStandby
			if not inStandby:
				message = _("%s update is about to start.\nDo you want to allow this?") % self.schedulename
				ybox = self.session.openWithCallback(self.doSchedule, MessageBox, message, MessageBox.TYPE_YESNO, timeout = 30)
				ybox.setTitle(_('%s scheduled update') % self.schedulename)
			else:
				self.doSchedule(True)
		self.scheduledate(atLeast)

	def doSchedule(self, answer):
		now = int(time())
		if answer is False:
			if self.config.retrycount.value < 2:
				print "[%s][doSchedule] Schedule delayed." % self.schedulename
				repeat = self.config.retrycount.value
				repeat += 1
				self.config.retrycount.value = repeat
				ScheduleTime = now + (int(self.config.retry.value) * 60)
				print "[%s][doSchedule] Time now set to" % self.schedulename, strftime("%c", localtime(ScheduleTime)), strftime("(now=%c)", localtime(now))
				self.scheduletimer.startLongTimer(int(self.config.retry.value) * 60)
			else:
				atLeast = 60
				print "[%s][doSchedule] Enough Retries, delaying till next schedule." % self.schedulename, strftime("%c", localtime(now))
				self.session.open(MessageBox, _("Enough Retries, delaying till next schedule."), MessageBox.TYPE_INFO, timeout = 10)
				self.config.retrycount.value = 0
				self.scheduledate(atLeast)
		else:
			self.timer = eTimer()
			self.timer.callback.append(self.doautostartscan)
			print "[%s][doSchedule] Running Schedule" % self.schedulename, strftime("%c", localtime(now))
			self.timer.start(100, 1)

	def doautostartscan(self):
		self.session.open(self.itemtorun)

	def doneConfiguring(self): # called from plugin on save
		now = int(time())
		if self.config.schedule.value:
			if autoScheduleTimer is not None:
				print "[%s][doneConfiguring] Schedule Enabled at" % self.schedulename, strftime("%c", localtime(now))
				autoScheduleTimer.scheduledate()
		else:
			if autoScheduleTimer is not None:
				global ScheduleTime
				ScheduleTime = 0
				print "[%s][doneConfiguring] Schedule Disabled at" % self.schedulename, strftime("%c", localtime(now))
				autoScheduleTimer.backupstop()
		if ScheduleTime > 0:
			t = localtime(ScheduleTime)
			scheduletext = strftime(_("%a %e %b  %-H:%M"), t)
		else:
			scheduletext = ""

