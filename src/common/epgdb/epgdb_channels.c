#include <stdio.h>
#include <strings.h>
#include <memory.h>
#include <malloc.h>
#include <stdlib.h>

#include "../../common.h"

#include "epgdb.h"
#include "epgdb_channels.h"

static epgdb_channel_t *channel_first = NULL;
static epgdb_channel_t *channel_last = NULL;

void epgdb_channels_reset ()
{
	channel_first = NULL;
	channel_last = NULL;
}

int epgdb_channels_count ()
{
	int count = 0;
	epgdb_channel_t *tmp = channel_first;
	
	while (tmp != NULL)
	{
		count++;
		tmp = tmp->next;
	}
	
	return count;
}

epgdb_channel_t *epgdb_channels_get_first () { return channel_first; }
void epgdb_channels_set_first (epgdb_channel_t *channel) { channel_first = channel; }
void epgdb_channels_set_last (epgdb_channel_t *channel) { channel_last = channel; }

epgdb_channel_t *epgdb_channels_get_by_freq (unsigned short int nid, unsigned short int tsid, unsigned short int sid)
{
	epgdb_channel_t *tmp = channel_first;
	
	while (tmp != NULL)
	{
		if ((nid == tmp->nid) && (tsid == tmp->tsid) && (sid == tmp->sid)) return tmp;
		
		tmp = tmp->next;
	}
	
	return NULL;
}

epgdb_channel_t *epgdb_channels_add (unsigned short int nid, unsigned short int tsid, unsigned short int sid, unsigned short int type)
{
	epgdb_channel_t *tmp = channel_first;
	
	while (tmp != NULL)
	{
		if ((nid == tmp->nid) && (tsid == tmp->tsid) && (sid == tmp->sid) && (type == tmp->type)) return tmp;
		tmp = tmp->next;
	}
	
	tmp = _malloc (sizeof (epgdb_channel_t));
	tmp->sid = sid;
	tmp->nid = nid;
	tmp->tsid = tsid;
	tmp->type = type;
	tmp->title_first = NULL;
	tmp->title_last = NULL;
	
	if (channel_last == NULL)
	{
		tmp->prev = NULL;
		tmp->next = NULL;
		channel_first = tmp;
		channel_last = tmp;
	}
	else
	{
		channel_last->next = tmp;
		tmp->prev = channel_last;
		tmp->next = NULL;
		channel_last = tmp;
	}
	
	return tmp;
}
