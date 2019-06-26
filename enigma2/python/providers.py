from Tools.Directories import crawlDirectory, fileExists

import re

emulator_path = "/usr/radiotimes_emulator"
epg_import_sources_path = "/etc/epgimport"

class Providers():
	def providerFileExists(self, key):
		filename = "%s/providers/%s.conf" % (emulator_path, key)
		return fileExists(filename)

	def getConf(self, key):
		filename = "%s/providers/%s.conf" % (emulator_path, key)
		try:
			f = open(filename, "r")
			conf = f.readlines()
			f.close()
			return conf
		except:
			print "[RadioTimesEmulatorGUI][providers] could not open %s" % filename

	def getName(self, lines):
		name_pattern = re.compile(r"description=(.+)")
		for line in lines:
			desc = re.search(name_pattern, line.strip())
			if desc:
				return desc.group(1).strip()

	def getTransponder(self, lines):
		transponder = {}
		transponder_keys = [
				"frequency",
				"symbol_rate",
				"polarization",
				"fec_inner",
				"orbital_position",
				"inversion",
				"system",
				"modulation",
				"roll_off",
				"pilot",
			]
		pattern = re.compile(r"(.*)=([0-9]+)")
		for line in lines:
			parm = re.search(pattern, line.strip())
			if parm and parm.group(1).strip() in transponder_keys:
				transponder[parm.group(1).strip()] = int(parm.group(2))
				if len(transponder) == len(transponder_keys):
					return transponder

	def read(self):
		providers = {}
		keys = [provider[1][:-5] for provider in crawlDirectory("%s/providers/" % (emulator_path), ".*\.conf$")]
		name_pattern = re.compile(r"description=([#].*)")
		for key in keys:
			conf = self.getConf(key)
			if not conf:
				continue
			name = self.getName(conf)
			transponder = self.getTransponder(conf)
			if name and transponder:
				providers[key] = {"name": name, "transponder": transponder}
		return providers


class ProviderConfig():
	def __init__(self, value = ""):
		self.provider = value

	def isValid(self):
		return len(self.provider) > 0

	def getProvider(self):
		return self.provider

	def setProvider(self, value):
		self.provider = value

	def serialize(self):
		return "%s" % (self.provider)
