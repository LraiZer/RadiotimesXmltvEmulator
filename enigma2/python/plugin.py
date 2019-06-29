# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.config import config, ConfigClock, configfile, ConfigNumber, ConfigSubsection, ConfigSelection, ConfigText, ConfigYesNo, getConfigListEntry, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.NimManager import nimmanager
from Components.Sources.StaticText import StaticText

from Plugins.Plugin import PluginDescriptor

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from Tools.BoundFunction import boundFunction
from Tools.Directories import pathExists

from os import statvfs # to get disc free space

try:
	from boxbranding import getImageDistro
except:
	def getImageDistro():
		return "UNKNOWN"

# from this plugin
from providers import Providers, emulator_path, epg_import_sources_path, ProviderConfig
from RadioTimesEmulator import RadioTimesEmulator
from RadioTimesEmulatorSchedule import AutoScheduleTimer, Scheduleautostart
from about import RadioTimesEmulatorAbout

paths = []
default_path = ""

def updatePaths():
	global paths
	global default_path
	# some images return the mount point with a trailing slash, others don't. Use map to make sure the slash is added where it is not present
	paths = ["/tmp/"] + map(lambda x: x.endswith("/") and x or "%s/" % x, [part.mountpoint for part in harddiskmanager.getMountedPartitions() if pathExists(part.mountpoint) and not part.mountpoint == "/" and not part.mountpoint.startswith('/media/net') and not part.mountpoint.startswith('/media/autofs')]) # no remote paths
	default_path = "/media/hdd/" if "/media/hdd/" in paths else "/tmp/"

updatePaths()

config.plugins.RadioTimesEmulator = ConfigSubsection()
config.plugins.RadioTimesEmulator.database_location = ConfigSelection(default=default_path, choices=paths)
config.plugins.RadioTimesEmulator.providers = ConfigText("", False)
config.plugins.RadioTimesEmulator.no_dvb_polling = ConfigYesNo(default=False)
config.plugins.RadioTimesEmulator.carousel_dvb_polling = ConfigYesNo(default=False)
config.plugins.RadioTimesEmulator.schedule = ConfigYesNo(default = False)
config.plugins.RadioTimesEmulator.scheduletime = ConfigClock(default = 0) # 1:00
config.plugins.RadioTimesEmulator.repeattype = ConfigSelection(default = "daily", choices = [("daily", _("Daily")), ("every 3 days", _("Every 3 days")), ("weekly", _("Weekly"))]) #
config.plugins.RadioTimesEmulator.retry = ConfigNumber(default = 30)
config.plugins.RadioTimesEmulator.retrycount = NoSave(ConfigNumber(default = 0))

def onPartitionChange(why, part):
	if why == 'add':
		onMountpointAdded(part.mountpoint)
	elif why == 'remove':
		onMountpointRemoved(part.mountpoint)

def onMountpointAdded(mountpoint):
	global paths
	global default_path
	if mountpoint not in paths:
		paths.append(mountpoint)
		config.plugins.RadioTimesEmulator.database_location.setChoices(choices=paths, default=default_path)

def onMountpointRemoved(mountpoint):
	global paths
	global default_path
	pathRemoved = config.plugins.RadioTimesEmulator.database_location.value == mountpoint
	if mountpoint in paths:
		paths.remove(mountpoint)
	if mountpoint == default_path:
		default_path = "/tmp/"
	config.plugins.RadioTimesEmulator.database_location.setChoices(choices=paths, default=default_path)
	if pathRemoved:
		config.plugins.RadioTimesEmulator.database_location.value = default_path
		config.plugins.RadioTimesEmulator.database_location.save()
		configfile.save()

harddiskmanager.on_partition_list_change.append(onPartitionChange)


class RadioTimesEmulatorGUIScreen(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _('Radio Times Emulator') + " - " + _('Setup')
		Screen.setTitle(self, self.setup_title)
		self.skinName = ["RadioTimesEmulatorGUIScreen", "Setup"]
		self.onChangedEntry = []
		self.session = session
		ConfigListScreen.__init__(self, [], session = session, on_change = self.changedEntry)

		self["actions2"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"menu": self.keyCancel,
			"cancel": self.keyCancel,
			"save": self.keySave,
			"red": self.keyCancel,
			"green": self.keySave,
			"yellow": self.keyGo,
			"blue": self.keyDelete
		}, -2)

		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Download"))
		self["key_blue"] = StaticText(_("About"))

		self["description"] = Label("")

		self.transponders = []
		self.session.postScanService = self.session.nav.getCurrentlyPlayingServiceOrGroup()

		self.prepare()
		
		self.createSetup()

		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def prepare(self):
		self.providers = Providers().read()
		self.providers_configs = {}
		self.orbital_supported = []

		# get supported orbital positions
		dvbs_nims = nimmanager.getNimListOfType("DVB-S")
		for nim in dvbs_nims:
			sats = nimmanager.getSatListForNim(nim)
			for sat in sats:
				if sat[0] not in self.orbital_supported:
					self.orbital_supported.append(sat[0])

		# read providers configurations
		providers_tmp_configs = {}
		providers_tmp = config.plugins.RadioTimesEmulator.providers.value.split("|")
		for provider_tmp in providers_tmp:
			provider_config = ProviderConfig(provider_tmp)

			if not provider_config.isValid():
				continue
			if provider_config.getProvider() not in self.providers:
				continue
			if self.providers[provider_config.getProvider()]["transponder"]["orbital_position"] not in self.orbital_supported:
				continue
			providers_tmp_configs[provider_config.getProvider()] = provider_config

		# build providers configurations
		for provider in self.providers.keys():
			self.providers_configs[provider] = ConfigYesNo(default = provider in providers_tmp_configs.keys())

	def providerKeysInNameOrder(self, providers):
		temp = []
		for provider in providers.keys():
			temp.append((provider, providers[provider]["name"]))
		return [i[0] for i in sorted(temp, key=lambda p: p[1].lower().decode('ascii','ignore'))]		

	def createSetup(self):
		indent = "- "
		self.list = []
		self.providers_enabled = []
		self.list.append(getConfigListEntry(_("Database location"), config.plugins.RadioTimesEmulator.database_location, _('Select the path where you want to save the files created by Radio Times Xmltv Emulator. The files will be read from this location. Locating the database in "/tmp/" means it will be lost on reboots.')))
		for provider in self.providerKeysInNameOrder(self.providers):
			if self.providers[provider]["transponder"]["orbital_position"] not in self.orbital_supported:
				continue
			self.list.append(getConfigListEntry(self.providers[provider]["name"], self.providers_configs[provider], _("This option enables fetching EPG data for the currently selected provider.")))
			self.providers_enabled.append(provider)
		self.list.append(getConfigListEntry(_("No dvb polling"), config.plugins.RadioTimesEmulator.no_dvb_polling, _('Only select this option if you fully understand why you need it, otherwise leave it "off".')))
		self.list.append(getConfigListEntry(_("Carousel dvb polling"), config.plugins.RadioTimesEmulator.carousel_dvb_polling, _('Only select this option if you fully understand why you need it, otherwise leave it "off".')))
		self.list.append(getConfigListEntry(_("Scheduled scan"), config.plugins.RadioTimesEmulator.schedule, _("Set up a task scheduler to automatically download the EPG data.")))
		if config.plugins.RadioTimesEmulator.schedule.value:
			self.list.append(getConfigListEntry(indent + _("Schedule time of day"), config.plugins.RadioTimesEmulator.scheduletime, _("Set the time of day to perform the EPG scan.")))
			self.list.append(getConfigListEntry(indent + _("Schedule repeat interval"), config.plugins.RadioTimesEmulator.repeattype, _("Set how often the scan should be done.")))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()

		config_string = ""
		for provider in self.providers_enabled:
			if self.providers_configs[provider].value:
				if len(config_string) > 0:
					config_string += "|"
				provider_config = ProviderConfig()
				provider_config.setProvider(provider)
				config_string += provider_config.serialize()
				
		config.plugins.RadioTimesEmulator.providers.value = config_string
		config.plugins.RadioTimesEmulator.providers.save()
		config.plugins.RadioTimesEmulator.database_location.save()
		configfile.save()
		try:
			AutoScheduleTimer.instance.doneConfiguring()
		except AttributeError as e:
			print "[RadioTimesEmulator] Timer.instance not available for reconfigure.", e

	def selectionChanged(self):
		self["description"].setText(self["config"].getCurrent()[2])

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		if self["config"].getCurrent() and len(self["config"].getCurrent()) > 1 and self["config"].getCurrent()[1] == config.plugins.RadioTimesEmulator.schedule:
			self.createSetup()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def keyGo(self):
		self.saveAll()
		self.startDownload()

	def startDownload(self):
		self.session.openWithCallback(self.RadioTimesEmulatorCallback, RadioTimesEmulator, {})

	def RadioTimesEmulatorCallback(self, answer=None):
		print "[RadioTimesEmulatorGUI]answer", answer
#		self.session.nav.playService(self.session.postScanService)
#		if answer:
#			self.close(True)
		self["description"].setText(_("The download has completed.") + " " +  _("Please don't forget that after downloading the first time the selected providers will need to be enabled in EPG-Importer plugin."))

	def keySave(self):
		self.saveAll()
		self["description"].setText(_("The current configuration has been saved.") + " " +  _("Please don't forget that after downloading the first time the selected providers will need to be enabled in EPG-Importer plugin."))

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelCallback, MessageBox, _("Really close without saving settings?"))
		else:
			self.cancelCallback(True)

	def cancelCallback(self, answer):
		if answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close(False)

	def getMountpointFreeSpaceMB(path):
		try:
			stat = statvfs(path)
		except OSError:
			return -1
		try:
			return (stat.f_bfree * stat.f_bsize) >> 20
		except:
			# occurs when f_blocks is 0 or a similar error
			return -1

	def keyDelete(self):
		self.session.open(RadioTimesEmulatorAbout)
		#pass


def RadioTimesEmulatorGUIStart(menuid, **kwargs):
	if menuid == "epg_menu" and getImageDistro() in ("teamblue",) or menuid == "epg":
		return [(_("Radio Times Emulator OpenTV Import"), RadioTimesEmulatorGUIMain, "RadioTimesEmulatorGUIScreen", 1000, True)]
	return []

def start_from_plugins_menu(session, **kwargs):
    session.open(RadioTimesEmulatorGUIScreen)

def RadioTimesEmulatorGUIMain(session, close=None, **kwargs):
	session.openWithCallback(boundFunction(RadioTimesEmulatorGUICallback, close), RadioTimesEmulatorGUIScreen)

def RadioTimesEmulatorGUICallback(close, answer):
	if close and answer:
		close(True)

def Plugins(**kwargs):
	name = _("Radio Times Emulator OpenTV Downloader")
	description = _("Creates XML files from OpenTV for use by EPG-Import plugin")
	pList = []
	if pathExists(emulator_path) or any([nimmanager.hasNimType(x) for x in ["DVB-S"]]):
		pList.append(PluginDescriptor(name="RadioTimesEmulatorSessionStart", where=PluginDescriptor.WHERE_SESSIONSTART, fnc=Scheduleautostart, needsRestart=True))
		pList.append(PluginDescriptor(name=name, description=description, where=PluginDescriptor.WHERE_MENU, fnc=RadioTimesEmulatorGUIStart, needsRestart=True) )
		if getImageDistro() in ("UNKNOWN",):
			pList.append(PluginDescriptor(name=name, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, fnc=start_from_plugins_menu, needsRestart=True))
	else:
		print "[RadioTimesEmulatorGUI] RadioTimesEmulator appears to be missing or no DVB-S tuner available."
	return pList
