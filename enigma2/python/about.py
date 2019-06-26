from Screens.Screen import Screen

from Components.Label import Label
from Components.ActionMap import ActionMap

class RadioTimesEmulatorAbout(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Radio Times Emulator GUI") + " - " + _("About"))
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
			"Radio Times Emulator Gui (c) 2019 \n",
			"https://github.com/oe-alliance/oe-alliance-plugins\n",
			"http://www.world-of-satellite.com\n\n",
			"Application credits:\n",
			"- Huevos (GUI developer)\n",
			"- Abu Baniaz (requesting and testing)\n\n",
			"Sources credits:\n",
			"- Radio Times Xmltv Emulator binary\n",
			"- LraiZer (binary developer)\n",
			"- https://github.com/LraiZer/RadiotimesXmltvEmulator/\n",
			"- Binary derived from CrossEPG open source code\n",
		]
		self["config"].setText(''.join(credits))

	def keyCancel(self):
		self.close()

