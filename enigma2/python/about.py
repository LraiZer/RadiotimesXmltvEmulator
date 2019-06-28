from Screens.Screen import Screen

from Components.Label import Label
from Components.ActionMap import ActionMap

class RadioTimesEmulatorAbout(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Radio Times Emulator") + " - " + _("About"))
		self.skinName = ["RadioTimesEmulatorAbout", "Setup"]

		self["config"] = Label("")

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions"],
		{
			"red": self.keyCancel,
			"cancel": self.keyCancel,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = Label(_("Exit"))

		credits = [
			"Radio Times Emulator Plugin (c) 2019\n",
			"https://github.com/LraiZer/RadiotimesXmltvEmulator/\n",
			"http://www.world-of-satellite.com\n\n",
			"Application credits:\n",
			"- LraiZer (binary developer)\n",
			"- Huevos (GUI developer)\n",
			"- Abu Baniaz (requesting and testing)\n\n",
			"Sources credits:\n",
			"- Binary derived from CrossEPG open source code\n",
			"- https://github.com/oe-alliance/e2openplugin-CrossEPG\n",
		]
		self["config"].setText(''.join(credits))

	def keyCancel(self):
		self.close()
