#include <stdio.h>
#include <strings.h>
#include <memory.h>
#include <malloc.h>
#include <stdlib.h>

#include "../../common.h"

#include "../core/log.h"

#include "providers.h"

static int channels_pids[1] = {0x11};
static int channels_pids_count = 1;
static int titles_pids[8] = {0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37};
static int titles_pids_count = 8;
static int summaries_pids[8] = {0x40,0x41,0x42,0x43,0x44,0x45,0x46,0x47};
static int summaries_pids_count = 8;
static int channels_types[64];
static int channels_types_count = 0;
static int nid = 0;
static int tsid = 0;
static int sid = 0;
static int orbital_position = 0;
static char provider_lang[2] = {'e','n'};

int  *providers_get_channels_pids() { return channels_pids;}
int  *providers_get_titles_pids() { return titles_pids;}
int  *providers_get_summaries_pids() { return summaries_pids;}
int  *providers_get_channels_types() { return channels_types;}
int  providers_get_nid() { return nid; }
int  providers_get_tsid() { return tsid; }
int  providers_get_sid() { return sid; }
int  providers_get_channels_pids_count() { return channels_pids_count;}
int  providers_get_titles_pids_count() { return titles_pids_count;}
int  providers_get_summaries_pids_count() { return summaries_pids_count;}
int  providers_get_channels_types_count() { return channels_types_count;}
int  providers_get_orbital_position() { return orbital_position; }
char *providers_get_lang() { return provider_lang;}

static char *providers_trim_spaces (char *text)
{
	char *tmp = text;
	while (tmp[0] == ' ') tmp++;
	while (strlen (tmp) > 1)
		if (tmp[strlen (tmp) - 1] == ' ') tmp[strlen (tmp) - 1] = '\0';
		else break;
	
	if (tmp[0] == ' ') tmp[0] = '\0';
	return tmp;
}

bool providers_read (char *read)
{
	FILE *fd = NULL;
	char line[512];
	char key[256];
	char value[256];
	
	channels_types_count = 0;

	fd = fopen (read, "r");
	if (!fd) 
		return false;
	
	while (fgets (line, sizeof(line), fd)) 
	{
		char *tmp_key, *tmp_value;
		
		memset (key, 0, sizeof (key));
		memset (value, 0, sizeof (value));
		
		if (sscanf (line, "%[^#=]=%[^\t\n]\n", key, value) != 2)
			continue;

		tmp_key = providers_trim_spaces (key);
		tmp_value = providers_trim_spaces (value);

		if (strcmp ("channels_types", tmp_key) == 0)
		{
			char* tmp = strtok (tmp_value, "|");
			while ((tmp != NULL) && (channels_types_count < 64))
			{
				channels_types[channels_types_count] = atoi (tmp);
				tmp = strtok (NULL, "|");
				channels_types_count++;
			}
		}
		else if (strcmp ("nid", tmp_key) == 0)
			nid = atoi (tmp_value);
		else if (strcmp ("tsid", tmp_key) == 0)
			tsid = atoi (tmp_value);
		else if (strcmp ("sid", tmp_key) == 0)
			sid = atoi (tmp_value);
		else if (strcmp ("orbital_position", tmp_key) == 0)
			orbital_position = atoi (tmp_value);
		else if (strcmp ("lang", tmp_key) == 0)
			strcpy(provider_lang, tmp_value);

	}
	
	fclose (fd);
	
	return true;
}
