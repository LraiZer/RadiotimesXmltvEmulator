#include <stdio.h>
#include <strings.h>
#include <memory.h>
#include <malloc.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/stat.h>

#include "../../common.h"

#include "epgdb.h"
#include "epgdb_channels.h"
#include "epgdb_titles.h"

typedef struct epgdb_channel_header_s
{
	uint16_t	nid;
	uint16_t	tsid;
	uint16_t	sid;
	uint16_t	type;
} epgdb_channel_header_t;

typedef struct epgdb_title_header_s
{
	uint16_t	event_id;
	uint16_t	mjd;
	uint32_t	start_time;
	uint16_t	length;
	uint8_t		genre_id;
	uint16_t	description_length;
	uint16_t	long_description_length;
	uint8_t		revision;

} epgdb_title_header_t;

void epgdb_clean ()
{
	epgdb_channel_t *channel = epgdb_channels_get_first ();
	
	while (channel != NULL)
	{
		epgdb_channel_t *tmp = channel;
		channel = channel->next;
		epgdb_title_t *title = tmp->title_first;
		
		while (title != NULL)
		{
			epgdb_title_t *tmp2 = title;
			title = title->next;
			_free (tmp2);
		}
		
		_free (tmp);
	}
	epgdb_channels_reset ();
}

