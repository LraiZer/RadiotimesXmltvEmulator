from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.config import config
from Components.Label import Label
from Components.NimManager import nimmanager
from Components.ProgressBar import ProgressBar
from Components.Sources.Progress import Progress
from Components.Sources.FrontendStatus import FrontendStatus

from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from Tools.Directories import pathExists

from enigma import eDVBResourceManager, eTimer, eDVBFrontendParameters, eDVBFrontendParametersSatellite

# from this plugin
from .providers import Providers, emulator_path, epg_import_sources_path, ProviderConfig
from .RadioTimesEmulatorSkin import downloadBar

import re
import sys

PY3 = sys.version_info.major >= 3
if PY3:
	import six


class RadioTimesEmulator(Screen):
	skin = downloadBar

	def __init__(self, session, args=0):
		print("[RadioTimesEmulator][__init__] Starting...")
		print("[RadioTimesEmulator][__init__] args", args)
		self.session = session
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Radio Times Emulator Download"))

		from Screens.Standby import inStandby
		if not inStandby:
			self["action"] = Label(_("Starting downloader"))
			self["status"] = Label("")
			self["progress"] = ProgressBar()
			self["progress_text"] = Progress()
			self["tuner_text"] = Label("")

		self["actions"] = ActionMap(["SetupActions"],
		{
			"cancel": self.keyCancel,
		}, -2)

		self.selectedNIM = -1
		if args:
			pass
		self.frontend = None
		from Screens.Standby import inStandby
		if not inStandby:
			self["Frontend"] = FrontendStatus(frontend_source=lambda: self.frontend, update_interval=100)
		self.rawchannel = None
		# self.session.postScanService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.postScanService = None
		self.index = 0
		self.LOCK_TIMEOUT_ROTOR = 1200  # 100ms for tick - 120 sec
		self.LOCK_TIMEOUT_FIXED = 50  # 100ms for tick - 5 sec

		self.LOCK_TIMEOUT = self.LOCK_TIMEOUT_FIXED
		self.databaseLocation = "%sradiotimes" % config.plugins.RadioTimesEmulator.database_location.value
		self.providers = Providers().read()
		self.onClose.append(self.__onClose)
		self.onFirstExecBegin.append(self.firstExec)

	def showError(self, message):
		if self.postScanService:
			self.session.nav.playService(self.postScanService)
			self.postScanService = None
		from Screens.Standby import inStandby
		if not inStandby:
			question = self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)
			question.setTitle(_("Radio Times Emulator Downloader"))
		self.close()

	def keyCancel(self):
		self.close()

	def firstExec(self):
		self.selectedProviders = {}
		self.actionsList = []

		providers_tmp = config.plugins.RadioTimesEmulator.providers.value.split("|")

		for provider_tmp in providers_tmp:
			provider_config = ProviderConfig(provider_tmp)
			if provider_config.isValid() and Providers().providerFileExists(provider_config.getProvider()):
				self.actionsList.append(provider_config.getProvider())
				self.selectedProviders[provider_config.getProvider()] = provider_config

		if len(self.actionsList) > 0:
			from Screens.Standby import inStandby
			if not inStandby:
				self["action"].setText(_('Starting download...'))
				self["status"].setText("")
			self.progresscount = len(self.actionsList) * 4 + 2
			self.progresscurrent = 1
			from Screens.Standby import inStandby
			if not inStandby:
				self["progress_text"].range = self.progresscount
				self["progress_text"].value = self.progresscurrent
				self["progress"].setRange((0, self.progresscount))
				self["progress"].setValue(self.progresscurrent)
			self.timer = eTimer()
			self.timer.callback.append(self.readStreams)
			self.timer.start(100, 1)
		else:
			self.showError(_('No providers to search. Please select at least one provider in the setup menu.'))

	def readStreams(self):
		if self.index < len(self.actionsList):  # some providers still need to be read
			self.transpondercurrent = self.getTransponder(self.providers[self.actionsList[self.index]]["transponder"])
			from Screens.Standby import inStandby
			if not inStandby:
				self["progress_text"].value = self.progresscurrent
				self["progress"].setValue(self.progresscurrent)
				self["action"].setText(_("Tuning %s, %s MHz") % (self.providers[self.actionsList[self.index]]["name"], str(self.transpondercurrent.frequency // 1000)))
				self["status"].setText("")
			self.searchtimer = eTimer()
			self.searchtimer.callback.append(self.getFrontend)
			self.searchtimer.start(100, 1)
		else:  # all providers have been read.
			self.closeFrontend()
			if self.postScanService:
				self.session.nav.playService(self.postScanService)
				self.postScanService = None
			self.progresscurrent += 1
			from Screens.Standby import inStandby
			if not inStandby:
				self["progress_text"].value = self.progresscurrent
				self["progress"].setValue(self.progresscurrent)
				self["action"].setText(_('Download successfully completed!'))
			self.closetimer = eTimer()
			self.closetimer.callback.append(self.close)
			self.closetimer.start(2000, 1)

	def getTransponder(self, tp):
		PLS_Default_Gold_Code = hasattr(eDVBFrontendParametersSatellite, "PLS_Default_Gold_Code") and eDVBFrontendParametersSatellite.PLS_Default_Gold_Code or 0  # Hack for OpenPLi 7.0
		parm = eDVBFrontendParametersSatellite()
		parm.frequency = tp["frequency"]
		parm.symbol_rate = tp["symbol_rate"]
		parm.polarisation = tp["polarization"]
		parm.fec = tp.get("fec_inner", eDVBFrontendParametersSatellite.FEC_Auto)
		parm.inversion = tp.get("inversion", eDVBFrontendParametersSatellite.Inversion_Unknown)
		parm.orbital_position = tp["orbital_position"]
		parm.system = tp.get("system", eDVBFrontendParametersSatellite.System_DVB_S)
		parm.modulation = tp.get("modulation", eDVBFrontendParametersSatellite.Modulation_QPSK)
		parm.rolloff = tp.get("rolloff", eDVBFrontendParametersSatellite.RollOff_alpha_0_35)
		parm.pilot = tp.get("pilot", eDVBFrontendParametersSatellite.Pilot_Unknown)
		parm.is_id = tp.get("is_id", eDVBFrontendParametersSatellite.No_Stream_Id_Filter)
		parm.pls_mode = tp.get("pls_mode", eDVBFrontendParametersSatellite.PLS_Gold)
		parm.pls_code = tp.get("pls_code", PLS_Default_Gold_Code)
		if hasattr(parm, "t2mi_plp_id"):
			parm.t2mi_plp_id = tp.get("t2mi_plp_id", eDVBFrontendParametersSatellite.No_T2MI_PLP_Id)
		if hasattr(parm, "t2mi_pid"):
			parm.t2mi_pid = tp.get("t2mi_pid", eDVBFrontendParametersSatellite.T2MI_Default_Pid)
		return parm

	def isRotorSat(self, slot, orb_pos):
		rotorSatsForNim = nimmanager.getRotorSatListForNim(slot)
		if len(rotorSatsForNim) > 0:
			for sat in rotorSatsForNim:
				if sat[0] == orb_pos:
					return True
		return False

	def getFrontend(self):
		print("[RadioTimesEmulator][getFrontend] searching for available tuner")
		nimList = []
		for nim in nimmanager.nim_slots:
			if not nim.isCompatible("DVB-S") or \
				nim.isFBCLink() or \
				(hasattr(nim, 'config_mode_dvbs') and nim.config_mode_dvbs or nim.config_mode) in ("loopthrough", "satposdepends", "nothing") or \
				self.transpondercurrent.orbital_position not in [sat[0] for sat in nimmanager.getSatListForNim(nim.slot)]:
				continue
			nimList.append(nim.slot)

		if len(nimList) == 0:
			print("[RadioTimesEmulator][getFrontend] No compatible tuner found")
			self.showError(_('No compatible tuner found'))
			return

		resmanager = eDVBResourceManager.getInstance()
		if not resmanager:
			print("[RadioTimesEmulator][getFrontend] Cannot retrieve Resource Manager instance")
			self.showError(_('Cannot retrieve Resource Manager instance'))
			return

		# stop pip if running
		if self.session.pipshown:
			self.session.pipshown = False
			del self.session.pip
			print("[RadioTimesEmulator][getFrontend] Stopping PIP.")

		# stop currently playing service if it is using a tuner in ("loopthrough", "satposdepends")
		currentlyPlayingNIM = None
		currentService = self.session and self.session.nav.getCurrentService()
		frontendInfo = currentService and currentService.frontendInfo()
		frontendData = frontendInfo and frontendInfo.getAll(True)
		if frontendData is not None:
			currentlyPlayingNIM = frontendData.get("tuner_number", None)
			if currentlyPlayingNIM is not None and nimmanager.nim_slots[currentlyPlayingNIM].isCompatible("DVB-S"):
				nimConfigMode = hasattr(nimmanager.nim_slots[currentlyPlayingNIM], "config_mode_dvbs") and nimmanager.nim_slots[currentlyPlayingNIM].config_mode_dvbs or nimmanager.nim_slots[currentlyPlayingNIM].config_mode
				if nimConfigMode in ("loopthrough", "satposdepends"):
					self.postScanService = self.session.nav.getCurrentlyPlayingServiceReference()
					self.session.nav.stopService()
					currentlyPlayingNIM = None
					print("[RadioTimesEmulator][getFrontend] The active service was using a %s tuner, so had to be stopped (slot id %s)." % (nimConfigMode, currentlyPlayingNIM))
		del frontendInfo
		del currentService

		current_slotid = -1
		if self.rawchannel:
			del(self.rawchannel)

		self.frontend = None
		self.rawchannel = None

		nimList = [slot for slot in nimList if not self.isRotorSat(slot, self.transpondercurrent.orbital_position)] + [slot for slot in nimList if self.isRotorSat(slot, self.transpondercurrent.orbital_position)]  # If we have a choice of dishes try "fixed" before "motorised".
		for slotid in nimList:
			if current_slotid == -1:  # mark the first valid slotid in case of no other one is free
				current_slotid = slotid

			self.rawchannel = resmanager.allocateRawChannel(slotid)
			if self.rawchannel:
				print("[RadioTimesEmulator][getFrontend] Nim found on slot id %d with sat %s" % (slotid, nimmanager.getSatName(self.transpondercurrent.orbital_position)))
				current_slotid = slotid
				break

			if self.rawchannel:
				break

		if current_slotid == -1:
			print("[RadioTimesEmulator][getFrontend] No valid NIM found")
			self.showError(_('No valid NIM found for %s') % self.providers[self.actionsList[self.index]]["name"])
			return

		if not self.rawchannel:
			# if we are here the only possible option is to close the active service
			if currentlyPlayingNIM in nimList:
				slotid = currentlyPlayingNIM
				print("[RadioTimesEmulator][getFrontend] Nim found on slot id %d but it's busy. Stopping active service" % slotid)
				self.postScanService = self.session.nav.getCurrentlyPlayingServiceReference()
				self.session.nav.stopService()
				self.rawchannel = resmanager.allocateRawChannel(slotid)
				if self.rawchannel:
					print("[RadioTimesEmulator][getFrontend] The active service was stopped, and the NIM is now free to use.")
					current_slotid = slotid

			if not self.rawchannel:
				if self.session.nav.RecordTimer.isRecording():
					print("[RadioTimesEmulator][getFrontend] Cannot free NIM because a recording is in progress")
					self.showError(_('Cannot free NIM because a recording is in progress'))
					return
				else:
					print("[RadioTimesEmulator][getFrontend] Cannot get the NIM")
					self.showError(_('Cannot get the NIM'))
					return

		# set extended timeout for rotors
		self.motorised = False
		if self.isRotorSat(current_slotid, self.transpondercurrent.orbital_position):
			self.motorised = True
			self.LOCK_TIMEOUT = self.LOCK_TIMEOUT_ROTOR
			print("[RadioTimesEmulator][getFrontend] Motorised dish. Will wait up to %i seconds for tuner lock." % (self.LOCK_TIMEOUT // 10))
		else:
			self.LOCK_TIMEOUT = self.LOCK_TIMEOUT_FIXED
			print("[RadioTimesEmulator][getFrontend] Fixed dish. Will wait up to %i seconds for tuner lock." % (self.LOCK_TIMEOUT // 10))

		self.selectedNIM = current_slotid  # Remember for downloading SI tables

		from Screens.Standby import inStandby
		if not inStandby:
			self["tuner_text"].setText(chr(ord('A') + current_slotid))

		self.frontend = self.rawchannel.getFrontend()
		if not self.frontend:
			print("[RadioTimesEmulator][getFrontend] Cannot get frontend")
			self.showError(_('Cannot get frontend'))
			return

		self.demuxer_id = self.rawchannel.reserveDemux()
		if self.demuxer_id < 0:
			print("[RadioTimesEmulator][doTune] Cannot allocate the demuxer.")
			self.showError(_('Cannot allocate the demuxer.'))
			return

		params_fe = eDVBFrontendParameters()
		params_fe.setDVBS(self.transpondercurrent, False)

		# try:
		#     self.rawchannel.requestTsidOnid()
		# except (TypeError):
		#     # for compatibility with some third party images
		#     self.rawchannel.requestTsidOnid(self.gotTsidOnid)

		self.frontend.tune(params_fe)

		self.progresscurrent += 1
		from Screens.Standby import inStandby
		if not inStandby:
			self["progress_text"].value = self.progresscurrent
			self["progress"].setValue(self.progresscurrent)
		self.lockcounter = 0
		self.locktimer = eTimer()
		self.locktimer.callback.append(self.checkTunerLock)
		self.locktimer.start(100, 1)

	def checkTunerLock(self):
		self.dict = {}
		self.frontend.getFrontendStatus(self.dict)
		if self.dict["tuner_state"] == "TUNING":
			if self.lockcounter < 1:  # only show this once in the log per retune event
				print("[RadioTimesEmulator][checkTunerLock] TUNING")
		elif self.dict["tuner_state"] == "LOCKED":
			print("[RadioTimesEmulator][checkTunerLock] TUNER LOCKED")
			from Screens.Standby import inStandby
			if not inStandby:
				self["action"].setText(_("Reading EPG from %s MHz") % (str(self.transpondercurrent.frequency // 1000)))
				# self["status"].setText(_("???"))

			self.progresscurrent += 1
			from Screens.Standby import inStandby
			if not inStandby:
				self["progress_text"].value = self.progresscurrent
				self["progress"].setValue(self.progresscurrent)
			self.readTranspondertimer = eTimer()
			self.readTranspondertimer.callback.append(self.readTransponder)
			self.readTranspondertimer.start(1000, 1)
			return
		elif self.dict["tuner_state"] in ("LOSTLOCK", "FAILED"):
			print("[RadioTimesEmulator][checkTunerLock] TUNING FAILED")
			self.showError(_('Tune failure. Provider %s. %s MHz. Tuner %s') % (self.providers[self.actionsList[self.index]]["name"], str(self.transpondercurrent.frequency // 1000), chr(ord('A') + self.selectedNIM)))
			return

		self.lockcounter += 1
		if self.lockcounter > self.LOCK_TIMEOUT:
			print("[RadioTimesEmulator][checkTunerLock] Timeout for tuner lock")
			self.showError(_('Tuner lock timeout. Provider %s. %s MHz. Tuner %s') % (self.providers[self.actionsList[self.index]]["name"], str(self.transpondercurrent.frequency // 1000), chr(ord('A') + self.selectedNIM)))
			return
		self.locktimer.start(100, 1)

	def readTransponder(self):
		command = self.RadioTimesEmulatorCommand()
		print("[RadioTimesEmulator] command:", command)
		self.session.openWithCallback(
			self.readTransponderCallback,
			RadioTimesEmulatorDisplayOutput,
			_("Radio Times Emulator - Downloading %s") % self.providers[self.actionsList[self.index]]["name"],  # this shows as the cosole title if you use the default console screen as the display.
			[command],
			closeOnSuccess=True,
			prefix="%s: " % self.providers[self.actionsList[self.index]]["name"])

	def readTransponderCallback(self):
		self.progresscurrent += 1
		from Screens.Standby import inStandby
		if not inStandby:
			self["progress_text"].value = self.progresscurrent
			self["progress"].setValue(self.progresscurrent)
		if pathExists(epg_import_sources_path):
			src_filename = "%s/otv_%s.sources.xml" % (self.databaseLocation, self.actionsList[self.index])
			dest_filename = "%s/otv_%s.sources.xml" % (epg_import_sources_path, self.actionsList[self.index])
			try:
				with open(src_filename, "r") as s:
					with open(dest_filename, "w") as d:
						d.write(s.read())
						d.close()
					s.close()
			except IOError:
				print("[RadioTimesEmulator] failed to copy %s to %s" % (src_filename, dest_filename))
		self.progresscurrent += 1
		from Screens.Standby import inStandby
		if not inStandby:
			self["progress_text"].value = self.progresscurrent
			self["progress"].setValue(self.progresscurrent)
		self.index += 1
		self.readStreams()

# Usage:
#   ./radiotimes_emulator [options]
# Options:
#   -d db_root    radiotimes db root folder
#                 default: /tmp/xmltv
#   -x demuxer    dvb demuxer
#                 default: /dev/dvb/adapter0/demux0
#   -f frontend   dvb frontend
#                 default: 0
#   -l homedir    home directory
#                 default: .
#   -p provider   opentv provider
#                 default: skyuk_28.2
#   -k nice       see "man nice"
#   -c            carousel dvb polling
#   -n            no dvb polling"
#   -r            show progress
#   -y            debug mode for huffman dictionary (summaries)
#   -z            debug mode for huffman dictionary (titles)
#   -h            show this help

# If switches -c and -x are used together, the only part of -x that will be used is the adaptor number, demux number will be discarded.

	def RadioTimesEmulatorCommand(self):
		return "%s/radiotimes_emulator -d %s -p %s -x /dev/dvb/adapter0/demux%d -f %d%s%s%s" % (
			emulator_path,
			self.databaseLocation,
			self.actionsList[self.index],  # provider key
			self.demuxer_id,
			self.selectedNIM,
			config.plugins.RadioTimesEmulator.no_dvb_polling.value and " -n" or "",
			config.plugins.RadioTimesEmulator.carousel_dvb_polling.value and " -c" or "",
			" -r",
		)

	def closeFrontend(self):
		if self.frontend:
			self.frontend = None
			del(self.rawchannel)

	def __onClose(self):
		self.closeFrontend()


class RadioTimesEmulatorDisplayOutput(Console):
	skin = downloadBar

	def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False, prefix=""):
		Console.__init__(self, session, title, cmdlist, finishedCallback, closeOnSuccess)
		self.prefix = prefix
		from Screens.Standby import inStandby
		if not inStandby:
			self["actionLong"] = Label("")

	def dataAvail(self, str):
		from Screens.Standby import inStandby
		if not inStandby:
			# self["text"].appendText(str) # Appending to this variable crashes OpenATV (ScrollLabel.py) if the variable is not used in the skin
			if PY3:
				str_no_date = re.sub(r'[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+[:][0-9]+[:][0-9]+', '', six.ensure_str(str)).strip()
			else:
				str_no_date = re.sub(r'[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+[:][0-9]+[:][0-9]+', '', str).strip()
			if str_no_date:
				self["actionLong"].setText("%s%s" % (self.prefix, re.sub(r'\s\s+', ".. ", str_no_date)))
