OBJS += src/common/memory.o
OBJS += src/common/core/log.o
OBJS += src/common/core/dvb_text.o
OBJS += src/common/dvb/dvb.o
OBJS += src/common/opentv/opentv.o
OBJS += src/common/opentv/huffman.o
OBJS += src/common/providers/providers.o
OBJS += src/common/epgdb/epgdb.o
OBJS += src/common/epgdb/epgdb_channels.o
OBJS += src/common/epgdb/epgdb_titles.o

DOWNLOADER_OBJS += src/common/radiotimes_emulator.o

DOWNLOADER_BIN = bin/radiotimes_emulator

BIN_DIR = bin

TARGET_ARCH ?= mips

#CFLAGS += -g -Wall -Werror

all: clean $(DOWNLOADER_BIN)

$(BIN_DIR):
	mkdir -p $@

$(OBJS): $(BIN_DIR)
	$(CC) $(CFLAGS) -c -fpic -o $@ $(@:.o=.c)

$(DOWNLOADER_OBJS):
	$(CC) $(CFLAGS) -c -o $@ $(@:.o=.c)

$(DOWNLOADER_BIN): $(OBJS) $(DOWNLOADER_OBJS)
	$(CC) $(LDFLAGS) -o $@ $(OBJS) $(DOWNLOADER_OBJS)
	$(STRIP) $@

clean:
	rm -f $(OBJS) $(DOWNLOADER_OBJS) $(DOWNLOADER_BIN)

install-gui:
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/images
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/po
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ar/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/bg/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ca/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/cs/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/da/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/de/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/el/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/en/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/en_GB/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/es/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/et/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fa/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fi/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fr/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fy/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/he/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/hr/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/hu/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/is/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/it/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/lt/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/lv/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/nb/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/nl/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/no/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pl/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pt/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pt_BR/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ro/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ru/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sk/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sl/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sr/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sv/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/th/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/tr/LC_MESSAGES
	install -d $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/uk/LC_MESSAGES
	install -m 644 images/*.png $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/images/
	install -m 644 po/*.po $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/po/
	install -m 644 locale/ar/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ar/LC_MESSAGES/
	install -m 644 locale/bg/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/bg/LC_MESSAGES/
	install -m 644 locale/ca/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ca/LC_MESSAGES/
	install -m 644 locale/cs/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/cs/LC_MESSAGES/
	install -m 644 locale/da/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/da/LC_MESSAGES/
	install -m 644 locale/de/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/de/LC_MESSAGES/
	install -m 644 locale/el/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/el/LC_MESSAGES/
	install -m 644 locale/en/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/en/LC_MESSAGES/
	install -m 644 locale/en_GB/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/en_GB/LC_MESSAGES/
	install -m 644 locale/es/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/es/LC_MESSAGES/
	install -m 644 locale/et/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/et/LC_MESSAGES/
	install -m 644 locale/fa/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fa/LC_MESSAGES/
	install -m 644 locale/fi/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fi/LC_MESSAGES/
	install -m 644 locale/fr/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fr/LC_MESSAGES/
	install -m 644 locale/fy/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/fy/LC_MESSAGES/
	install -m 644 locale/he/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/he/LC_MESSAGES/
	install -m 644 locale/hr/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/hr/LC_MESSAGES/
	install -m 644 locale/hu/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/hu/LC_MESSAGES/
	install -m 644 locale/is/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/is/LC_MESSAGES/
	install -m 644 locale/it/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/it/LC_MESSAGES/
	install -m 644 locale/lt/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/lt/LC_MESSAGES/
	install -m 644 locale/lv/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/lv/LC_MESSAGES/
	install -m 644 locale/nb/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/nb/LC_MESSAGES/
	install -m 644 locale/nl/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/nl/LC_MESSAGES/
	install -m 644 locale/no/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/no/LC_MESSAGES/
	install -m 644 locale/pl/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pl/LC_MESSAGES/
	install -m 644 locale/pt/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pt/LC_MESSAGES/
	install -m 644 locale/pt_BR/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/pt_BR/LC_MESSAGES/
	install -m 644 locale/ro/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ro/LC_MESSAGES/
	install -m 644 locale/ru/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/ru/LC_MESSAGES/
	install -m 644 locale/sk/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sk/LC_MESSAGES/
	install -m 644 locale/sl/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sl/LC_MESSAGES/
	install -m 644 locale/sr/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sr/LC_MESSAGES/
	install -m 644 locale/sv/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/sv/LC_MESSAGES/
	install -m 644 locale/th/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/th/LC_MESSAGES/
	install -m 644 locale/tr/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/tr/LC_MESSAGES/
	install -m 644 locale/uk/LC_MESSAGES/RadioTimesEmulator.mo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/locale/uk/LC_MESSAGES/
	install -m 644 enigma2/python/*.py $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/
	install -m 644 enigma2/python/*.pyo $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/
	install -m 644 enigma2/python/LICENSE $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/
	install -m 644 enigma2/python/LICENSE.GPLv2 $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/
	install -m 644 enigma2/python/README.txt $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/
	install -m 644 ./Radio-Times-EPG-Emulator.pdf $(D)${libdir}/enigma2/python/Plugins/SystemPlugins/RadioTimesEmulator/

install-standalone:
	install -d $(D)/usr/radiotimes_emulator/providers
	install -m 755 bin/radiotimes_emulator $(D)/usr/radiotimes_emulator/
	install -m 644 providers/* $(D)/usr/radiotimes_emulator/providers/

install-standalone-var:
	install -d $(D)/var/radiotimes_emulator/providers
	install -m 755 bin/radiotimes_emulator $(D)/var/radiotimes_emulator/
	install -m 644 providers/* $(D)/var/radiotimes_emulator/providers/

install: install-standalone
install-var: install-standalone-var
install-var-flash: install-standalone-var
install-plugin: install-standalone install-gui

