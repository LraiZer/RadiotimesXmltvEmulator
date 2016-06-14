#include <stdio.h>
#include <strings.h>
#include <memory.h>
#include <malloc.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <stdint.h>

#include "../../common.h"

#include "epgdb.h"
#include "epgdb_titles.h"

epgdb_title_t *epgdb_title_alloc ()
{
	epgdb_title_t *ret = _malloc (sizeof (epgdb_title_t));
	ret->genre_id = 0;
	return ret;
}

void epgdb_title_free (epgdb_title_t *title)
{
	_free (title);
}

int epgdb_calculate_mjd (time_t value)
{
	return 40587 + ((value) / 86400.0);
}

int epgdb_titles_count (epgdb_channel_t *channel)
{
	int count = 0;
	epgdb_title_t *tmp = channel->title_first;
	
	while (tmp != NULL)
	{
		count++;
		tmp = tmp->next;
	}
	
	return count;
}

epgdb_title_t *epgdb_titles_get_by_id_and_mjd (epgdb_channel_t *channel, unsigned short int event_id, unsigned short int mjd_time)
{
	if (channel == NULL) return NULL;

	epgdb_title_t *tmp = channel->title_first;
	
	while (tmp != NULL)
	{
		if ((tmp->mjd == mjd_time) && (tmp->event_id == event_id)) break;
		tmp = tmp->next;
	}
	
	return tmp;
}

void epgdb_titles_delete_event_id (epgdb_channel_t *channel, unsigned short int event_id)
{
	if (channel == NULL) return;
	
	epgdb_title_t *tmp = channel->title_first;
	
	while (tmp != NULL)
	{
		if (tmp->event_id == event_id)
		{
			epgdb_title_t *tmp2 = tmp;
			if (tmp->prev != NULL) tmp->prev->next = tmp->next;
			if (tmp->next != NULL) tmp->next->prev = tmp->prev;
			if (tmp == channel->title_first) channel->title_first = tmp->next;
			if (tmp == channel->title_last) channel->title_last = tmp->prev;
			tmp = tmp->next;
			_free (tmp2);
		}
		else tmp = tmp->next;
	}
}

void epgdb_titles_delete_in_range (epgdb_channel_t *channel, time_t start_time, unsigned short int length)
{
	if (channel == NULL) return;
	
	epgdb_title_t *tmp = channel->title_first;
	
	while (tmp != NULL)
	{
		// do this check better
		if (!(((tmp->start_time + tmp->length) <= start_time) || (tmp->start_time >= (start_time + length))))
		{
			if (tmp->start_time != start_time)
			{
				epgdb_title_t *tmp2 = tmp;
				if (tmp->prev != NULL) tmp->prev->next = tmp->next;
				if (tmp->next != NULL) tmp->next->prev = tmp->prev;
				if (tmp == channel->title_first) channel->title_first = tmp->next;
				if (tmp == channel->title_last) channel->title_last = tmp->prev;
				tmp = tmp->next;
				_free (tmp2);
			}
			else tmp = tmp->next;
		}
		else tmp = tmp->next;
	}
}

epgdb_title_t *epgdb_titles_add (epgdb_channel_t *channel, epgdb_title_t *title)
{
	if (channel == NULL) return NULL;
	if (title == NULL) return NULL;
	
	epgdb_titles_delete_in_range (channel, title->start_time, title->length);
	
	title->description_length = 0;
	title->long_description_length = 0;
	title->changed = true;
	title->revision = 0;
	
	/* add into list */				
	if (channel->title_first == NULL)
	{
		title->next = NULL;
		title->prev = NULL;
		channel->title_first = title;
		channel->title_last = title;
	}
	else
	{
		epgdb_title_t *tmp = channel->title_first;
		while (true)
		{
			if (tmp->start_time == title->start_time)
			{
				if (tmp->length != title->length ||
					tmp->event_id != title->event_id ||
					tmp->genre_id != title->genre_id)
				{
					tmp->event_id = title->event_id;
					tmp->length = title->length;
					tmp->genre_id = title->genre_id;
					tmp->changed = true;
					tmp->revision++;
				}
				_free (title);
				title = tmp;
				break;
			}
			if (tmp->start_time > title->start_time)
			{
				title->prev = tmp->prev;
				title->next = tmp;
				title->next->prev = title;
				if (title->prev != NULL)
					title->prev->next = title;
				else
					channel->title_first = title;
				break;
			}
			
			if (tmp->next == NULL)
			{
				title->prev = tmp;
				title->next = NULL;
				title->prev->next = title;
				channel->title_last = title;
				break;
			}
			
			tmp = tmp->next;
		}
	}
	
	return title;
}
