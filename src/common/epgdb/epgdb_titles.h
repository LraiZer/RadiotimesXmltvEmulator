#ifndef _EPGDB_TITLES_H_
#define _EPGDB_TITLES_H_

epgdb_title_t *epgdb_title_alloc ();
void epgdb_title_free (epgdb_title_t *title);
int epgdb_calculate_mjd (time_t value);
int epgdb_titles_count (epgdb_channel_t *channel);
epgdb_title_t *epgdb_titles_get_by_id_and_mjd (epgdb_channel_t *channel, unsigned short int event_id, unsigned short int mjd_time);
epgdb_title_t *epgdb_titles_add (epgdb_channel_t *channel, epgdb_title_t *title);
void epgdb_titles_delete_event_id (epgdb_channel_t *channel, unsigned short int event_id);

#endif // _EPGDB_TITLES_H_
