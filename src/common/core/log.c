#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>

#include "../../common.h"

#include "log.h"

static FILE *fd = NULL;
static bool enabled = true;

void log_enable ()
{
	enabled = true;
}
void log_disable ()
{
	enabled = false;
}
bool log_new (char *db_root)
{
	char log_filename[256];
	sprintf (log_filename, "%s/%s.log", db_root, provider);

	fd = fopen (log_filename, "w");
	if (fd != NULL)
		fclose (fd);

	return (fd != NULL);
}

bool log_open (char *db_root)
{	
	char log_filename[256];
	sprintf (log_filename, "%s/%s.log", db_root, provider);

	fd = fopen (log_filename, "a");
	
	return (fd != NULL);
}

void log_banner (char *app_name)
{
	log_add ("\n\nRadiotimesXmltv Emulator -(beta)- BRANCH{e2xmltv}\nSources https://github.com/LraiZer/RadiotimesXmltvEmulator\n");
	log_add ("\nBased on SIFTeam Crossepg (c) 2009-2014 Sandro Cavazzoni\nSources https://github.com/oe-alliance/e2openplugin-CrossEPG\n");
	log_add ("\nSource credits: crossepg, tv_grab_dvb\n");
	log_add ("\nThis software is distributed under the terms of the,\nGNU Lesser General Public License v2.1\n");
}

void log_close ()
{
	if (fd != NULL)
		fclose (fd);
}

void log_add (char *message, ...)
{
	va_list args;
	char msg[16*1024];
	time_t now_time;
	struct tm *loctime;

	now_time = time (NULL);
	loctime = localtime (&now_time);
	strftime (msg, 255, "%d/%m/%Y %H:%M:%S ", loctime);
	
	if (enabled)
		fwrite (msg, strlen (msg), 1, stdout);
	if (fd != NULL) fwrite (msg, strlen (msg), 1, fd);

	va_start (args, message);
	vsnprintf (msg, 16*1024, message, args);
	va_end (args);
	msg[(16*1024)-1] = '\0';
	
	if (enabled)
	{
		fwrite (msg, strlen (msg), 1, stdout);
		fwrite ("\n", 1, 1, stdout);
		fflush (stdout);
	}

	if (fd != NULL)
	{
    	fwrite (msg, strlen (msg), 1, fd);
    	fwrite ("\n", 1, 1, fd);
    	fflush (fd);
	}
}
