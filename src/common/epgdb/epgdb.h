#ifndef _EPGDB_H_
#define _EPGDB_H_

#include <stdint.h>

#define DB_REVISION	0x07

#define FLAG_UTF8	0x01 // 0000 0001

#define SET_UTF8(x)	(x |= FLAG_UTF8)
#define UNSET_UTF8(x)	(x &= (~FLAG_UTF8))
#define IS_UTF8(x)	(x & FLAG_UTF8)

typedef struct epgdb_title_s
{
	/* same elements of epgdb_title_header_t */
	uint16_t	event_id;
	uint16_t	mjd;
	uint32_t	start_time;
	uint16_t	length;
	uint8_t		genre_id;
	uint16_t	description_length;
	uint16_t	long_description_length;
	uint8_t		revision;
	char		program[35];

	/* other elements */
	bool					changed;
	struct epgdb_title_s	*prev;
	struct epgdb_title_s	*next;
} epgdb_title_t;

typedef struct epgdb_channel_s
{
	/* same element of epgdb_channel_header_t */
	uint16_t	nid;
	uint16_t	tsid;
	uint16_t	sid;
	uint16_t	type;

	/* other elements */
	struct epgdb_channel_s	*prev;
	struct epgdb_channel_s	*next;
	struct epgdb_title_s 	*title_first;
	struct epgdb_title_s 	*title_last;
} epgdb_channel_t;

void epgdb_clean ();
#endif // _EPGDB_H_
