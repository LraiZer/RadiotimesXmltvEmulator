#include <stdio.h>
#include <time.h>
#include <memory.h>
#include <malloc.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "../../common.h"
#include "../core/log.h"
#include "../providers/providers.h"

#include "huffman.h"
#include "opentv.h"

#include "../epgdb/epgdb_channels.h"
#include "../epgdb/epgdb_titles.h"

#define MAX_GENRE_SIZE		0xFF
#define MAX_TITLE_SIZE		0xFF
#define MAX_SUMMARIE_SIZE	0x3FFF
#define MAX_CHANNELS		0xFFFF

static epgdb_channel_t *channels[MAX_CHANNELS];
char channels_name[MAX_CHANNELS][256];

static unsigned short int ch_count, ch_name_count;
static int tit_count;

void removeSubstring(char *s,const char *toremove)
{
  while( (s=strstr(s,toremove)) )
    memmove(s,s+strlen(toremove),1+strlen(s+strlen(toremove)));
}

char *replace_Substring(char *str, char *orig, char *rep, int start)
{
	static char temp[4096];
	static char buffer[4096];
	char *p;

	strcpy(temp, str + start);

	if(!(p = strstr(temp, orig)))
		return temp;

	strncpy(buffer, temp, p-temp);
	buffer[p-temp] = '\0';

	sprintf(buffer + (p - temp), "%s%s", rep, p + strlen(orig));
	sprintf(str + start, "%s", buffer);

	return str;
}

void opentv_init ()
{
	int i;
	ch_count = ch_name_count = tit_count = 0;
	for (i=0; i<MAX_CHANNELS; i++)
		channels[i] = NULL;
	for (i=0; i<MAX_GENRE_SIZE; i++)
		genre[i] = NULL;
}

void opentv_cleanup ()
{
	int i;
	for (i=0; i<256; i++)
	{
		if (genre[i] != NULL)
		{
			_free (genre[i]);
		}
	}
}

void opentv_read_channels_sdt (unsigned char *data, unsigned int length)
{
	int offset = 11;
	length -= 11;

	while (length >= 5)
	{
		unsigned short service_id = (data[offset] << 8) | data[offset + 1];
		//unsigned short free_ca = (data[offset + 3] >> 4) & 0x01;
		int descriptors_loop_length = ((data[offset + 3] & 0x0f) << 8) | data[offset + 4];
		char service_name[256];

		memset(service_name, '\0', 256);

		length -= 5;
		offset += 5;

		int offset2 = offset;

		length -= descriptors_loop_length;
		offset += descriptors_loop_length;

		while (descriptors_loop_length >= 2)
		{
			unsigned char descriptor_tag = data[offset2];
			unsigned char descriptor_length = data[offset2 + 1];

			if (descriptor_tag == 0x48)
			{
				int service_provider_name_length = data[offset2 + 3];
				if (service_provider_name_length == 255)
					service_provider_name_length--;

				int service_name_length = data[offset2 + 4 + service_provider_name_length];
				if (service_name_length == 255)
					service_name_length--;

				if (service_name_length > 0)
				{
					if (data[offset2 + 5 + service_provider_name_length] == 0x05)
					{
						service_provider_name_length++;
						service_name_length--;
					}
				}

				memcpy(service_name, data + offset2 + 5 + service_provider_name_length, service_name_length);
			}
			if (descriptor_tag == 0xc0)
				memcpy(service_name, data + offset2 + 2, descriptor_length);

			descriptors_loop_length -= (descriptor_length + 2);
			offset2 += (descriptor_length + 2);
		}

		if (channels_name[service_id][0] == '\0')
		{
			ch_name_count++;
			memcpy(channels_name[service_id], service_name, sizeof(service_name));
		}
	}
}

bool opentv_read_channels_bat (unsigned char *data, unsigned int length, char *db_root)
{
	unsigned short int bouquet_descriptors_length = ((data[8] & 0x0f) << 8) | data[9];
	unsigned short int transport_stream_loop_length = ((data[bouquet_descriptors_length + 10] & 0x0f) << 8) | data[bouquet_descriptors_length + 11];
	unsigned int offset1 = bouquet_descriptors_length + 12;
	bool ret = false;

	while (transport_stream_loop_length > 0)
	{
		unsigned int name_space = providers_get_orbital_position() << 16;
		unsigned short int tid = (data[offset1] << 8) | data[offset1 + 1];
		unsigned short int nid = (data[offset1 + 2] << 8) | data[offset1 + 3];
		unsigned short int transport_descriptor_length = ((data[offset1 + 4] & 0x0f) << 8) | data[offset1 + 5];
		unsigned int offset2 = offset1 + 6;

		// 7e3 tsid is unique in Enigma2 hardcoding for 282, we dont pull transponder data so hardcode current :(
		// Transport.name_space |= ((Transport.frequency/1000)*10) + Transport.polarization
		if (nid == 0x2 && tid == 0x7e3)
			name_space |= 0x2f26;

		offset1 += (transport_descriptor_length + 6);
		transport_stream_loop_length -= (transport_descriptor_length + 6);
		
		while (transport_descriptor_length > 0)
		{
			unsigned char descriptor_tag = data[offset2];
			unsigned char descriptor_length = data[offset2 + 1];
			unsigned int offset3 = offset2 + 2;
			
			offset2 += (descriptor_length + 2);
			transport_descriptor_length -= (descriptor_length + 2);

			if (descriptor_tag == 0xb1)
			{
				offset3 += 2;
				descriptor_length -= 2;
				while (descriptor_length > 0)
				{
					unsigned short int type_id;
					unsigned short int channel_id;
					unsigned short int sid;
					//unsigned short int sky_id;

					sid = (data[offset3] << 8) | data[offset3 + 1];
					type_id = data[offset3 + 2];
					channel_id = (data[offset3 + 3] << 8) | data[offset3 + 4];
					//sky_id = ( data[offset3+5] << 8 ) | data[offset3+6];

					if (channels[channel_id] == NULL)
					{
						FILE *outfile;
						char name_file[256];
						memset(name_file, '\0', 256);
						sprintf(name_file, "%s/%s.channels.xml", db_root, provider);
						outfile = fopen(name_file,"a");
						fprintf(outfile,"<!-- %s --><channel id=\"%i_%i_%i\">1:0:%X:%X:%X:%X:%X:0:0:0:</channel><!-- \"%s\" -->\n",
							provider,
							providers_get_orbital_position(), nid, channel_id,
							type_id,
							sid,
							tid,
							nid,
							name_space,
							channels_name[sid]);
						fflush(outfile);
						fclose(outfile);

						channels[channel_id] = epgdb_channels_add (nid, tid, sid, type_id);
						ch_count++;
						ret = true;
					}

					offset3 += 9;
					descriptor_length -= 9;
				}
			}
		}
	}
	return ret;
}

unsigned short opentv_channels_count()
{
	return ch_count;
}

unsigned short opentv_channels_name_count()
{
	return ch_name_count;
}

void opentv_read_titles (unsigned char *data, unsigned int length, bool huffman_debug)
{
	epgdb_title_t *title;
	unsigned short int channel_id = (data[3] << 8) | data[4];
	unsigned short int mjd_time = (data[8] << 8) | data[9];
	
	if ((channel_id > 0) && (mjd_time > 0))
	{
		unsigned int offset = 10;
		
		while ((offset + 11) < length)
		{
			unsigned short int event_id;
			unsigned char description_length;
			unsigned short int packet_length = ((data[offset + 2] & 0x0f) << 8) | data[offset + 3];
			
			if ((data[offset + 4] != 0xb5) || ((packet_length + offset) > length)) break;
			
			event_id = (data[offset] << 8) | data[offset + 1];
			offset += 4;
			description_length = data[offset + 1] - 7;
			
			if ((offset + 9 + description_length) > length) break;
			
			if (channels[channel_id] != NULL)
			{
				char tmp[256];
				
				/* prepare struct */
				title = _malloc (sizeof (epgdb_title_t));
				title->event_id = event_id;
				title->start_time = ((mjd_time - 40587) * 86400) + ((data[offset + 2] << 9) | (data[offset + 3] << 1));
				title->mjd = mjd_time;
				title->length = ((data[offset + 4] << 9) | (data[offset + 5] << 1));
				title->genre_id = data[offset + 6];
				
				if (!huffman_decode (data + offset + 9, description_length, tmp, MAX_TITLE_SIZE * 2, huffman_debug))
					tmp[0] = '\0';
				else
					tmp[35] = '\0';

				strcpy(title->program, tmp);
				title = epgdb_titles_add (channels[channel_id], title);

				if (huffman_debug)
				{
					char mtime[20];
					struct tm *loctime = localtime ((time_t*)&title->start_time);
					printf ("Nid: %x Tsid: %x Sid: %x Type: %x\n", channels[channel_id]->nid, channels[channel_id]->tsid, channels[channel_id]->sid, channels[channel_id]->type);
					strftime (mtime, 20, "%d/%m/%Y %H:%M", loctime);
					printf ("Start time: %s\n", mtime);
				}
					tit_count++;
			}

			offset += packet_length;
		}
	}
}

void opentv_read_summaries (unsigned char *data, unsigned int length, bool huffman_debug, char *db_root)
{
	if (length < 20) return;

	unsigned short int channel_id = (data[3] << 8) | data[4];
	unsigned short int mjd_time = (data[8] << 8) | data[9];
	
	if ((channel_id > 0) && (mjd_time > 0))
	{
		unsigned int offset = 10;

		while (offset + 4 < length)
		{
			unsigned short int event_id;
			int packet_length = ((data[offset + 2] & 0x0f) << 8) | data[offset + 3];
			int packet_length2 = packet_length;
			unsigned char buffer[MAX_SUMMARIE_SIZE];
			unsigned short int buffer_size = 0;
			unsigned int offset2;

			if (packet_length == 0) break;

			event_id = (data[offset] << 8) | data[offset + 1];
			offset += 4;
			offset2 = offset;
			while (packet_length2 > 0)
			{
				unsigned char descriptor_tag = data[offset2];
				unsigned char descriptor_length = data[offset2 + 1];

				offset2 += 2;

				if (descriptor_tag == 0xb9 &&
					MAX_SUMMARIE_SIZE > buffer_size + descriptor_length &&
					offset2 + descriptor_length < length)
				{
					memcpy(&buffer[buffer_size], &data[offset2], descriptor_length);
					buffer_size += descriptor_length;
				}

				packet_length2 -= descriptor_length + 2;
				offset2 += descriptor_length;
			}

			offset += packet_length;

			if (buffer_size > 0 && channels[channel_id] != NULL)
			{
				epgdb_title_t *title = epgdb_titles_get_by_id_and_mjd (channels[channel_id], event_id, mjd_time);
				if (title != NULL)
				{
					char tmp[MAX_SUMMARIE_SIZE * 2];
					if (!huffman_decode (buffer, buffer_size, tmp, MAX_SUMMARIE_SIZE * 2, huffman_debug))
						tmp[0] = '\0';
					else
						removeSubstring(tmp," Also in HD");

					if (huffman_debug)
					{
						char mtime[20];
						struct tm *loctime = localtime ((time_t*)&title->start_time);
						printf ("Nid: %x Tsid: %x Sid: %x Type: %x\n", channels[channel_id]->nid, channels[channel_id]->tsid, channels[channel_id]->sid, channels[channel_id]->type);
						strftime (mtime, 20, "%d/%m/%Y %H:%M", loctime);
						printf ("Start time: %s\n", mtime);
						
					}
/*
					// Keep current timestamp, we write the localtime() +0000/+0100 offset %z
					// OR convert to GMT, should set timestamp and localtime offset to +0000?

					char mtime_s[256];
					memset(mtime_s, '\0', 256);
					struct tm *loctime_s, *gmtime_s;
					loctime_s = localtime((time_t*)&title->start_time);
					time_t mytime_s = mktime(loctime_s);
					gmtime_s = gmtime(&mytime_s);
					strftime (mtime_s, sizeof(mtime_s), "%Y%m%d%H%M%S %z", gmtime_s);

					char mtime_e[256];
					struct tm *loctime_e, *gmtime_e;
					memset(mtime_e, '\0', 256);
					uint32_t endt = title->start_time + title->length;
					loctime_e = localtime((time_t*)&endt);
					time_t mytime_e = mktime(loctime_e);
					gmtime_e = gmtime(&mytime_e);
					strftime (mtime_e, sizeof(mtime_e), "%Y%m%d%H%M%S %z", gmtime_e);
*/

					char mtime_s[256];
					memset(mtime_s, '\0', 256);
					struct tm *loctime_s = localtime ((time_t*)&title->start_time);
					strftime (mtime_s, sizeof(mtime_s), "%Y%m%d%H%M%S %z", loctime_s);

					char mtime_e[256];
					memset(mtime_e, '\0', 256);
					uint32_t endt;
					endt = (title->start_time + title->length);
					struct tm *loctime_e = localtime ((time_t*)&endt);
					strftime (mtime_e, sizeof(mtime_e), "%Y%m%d%H%M%S %z", loctime_e);

					FILE *outfile;
					char name_file[256];
					memset(name_file, '\0', 256);
					sprintf(name_file, "%s/%s.xml", db_root, provider);
					outfile = fopen(name_file,"a");
					fprintf(outfile, " <programme start=\"%s\" stop=\"%s\" channel=\"%i_%i_%i\">\n", mtime_s, mtime_e, providers_get_orbital_position(), channels[channel_id]->nid, channel_id);
					fprintf(outfile, "  <title lang=\"%s\">%s</title>\n", providers_get_lang(), xmlify(title->program, strlen(title->program)));
					fprintf(outfile, "  <sub-title lang=\"%s\">%s</sub-title>\n", providers_get_lang(), xmlify(genre[title->genre_id], strlen(genre[title->genre_id])));
					fprintf(outfile, "  <desc lang=\"%s\">%s</desc>\n", providers_get_lang(), xmlify(tmp, strlen(tmp)));
					fprintf(outfile, " </programme>\n");
					fflush(outfile);
					fclose(outfile);

					epgdb_titles_delete_event_id(channels[channel_id], title->event_id);
				}
			}
		}
	}
}

bool opentv_read_themes (char *file)
{
	FILE *fd;
	char line[256];

	log_add ("Reading themes '%s'", file);

	fd = fopen (file, "r");
	if (!fd) 
	{
		log_add ("Error. Cannot open themes file");
		return false;
	}

	int genre_id = 0;
	char string1[256];
	char string2[256];

	while (fgets (line, sizeof(line), fd))
	{
		memset(string1, 0, sizeof(string1));
		memset(string2, 0, sizeof(string2));

		if(sscanf(line, "%[^=] =%[^\n] ", string1, string2) == 2)
		{
			genre[genre_id] = _malloc (sizeof (char) * (strlen (string2) + 1));
			snprintf((char *) genre[genre_id], 255, "%s", string2);
		}
		else
		{
			genre[genre_id] = _malloc (sizeof (char) * (strlen (string1) + 10));
			snprintf((char *) genre[genre_id], 255, "Genre %s", string1);
		}
		genre_id++;
	}
	fclose(fd);

	log_add ("Completed. Read %d values", genre_id);

	return true;
}

epgdb_channel_t *opentv_get_channel (unsigned short int id)
{
	return channels[id];
}
