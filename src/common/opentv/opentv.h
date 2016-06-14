#ifndef _OPENTV_H_
#define _OPENTV_H_

#include "../epgdb/epgdb.h"

char *genre[256];

void opentv_init ();
void opentv_cleanup ();
bool opentv_read_channels_bat (unsigned char *data, unsigned int length, char *db_root);
unsigned short opentv_channels_count ();
bool opentv_read_themes (char *file);
void opentv_free_themes ();
void opentv_read_titles (unsigned char *data, unsigned int length, bool huffman_debug);
void opentv_read_summaries (unsigned char *data, unsigned int length, bool huffman_debug, char *db_root);
epgdb_channel_t *opentv_get_channel (unsigned short int id);

#endif // _OPENTV_H_
