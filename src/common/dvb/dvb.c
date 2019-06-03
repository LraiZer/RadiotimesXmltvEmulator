#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
#include <stdarg.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#ifdef OLDDVBAPI
#include <ost/dmx.h>
#define dmx_pes_filter_params dmxPesFilterParams
#define dmx_sct_filter_params dmxSctFilterParams
#else
#include <linux/dvb/dmx.h>
/*
	get rid of DMX_SET_SOURCE patch dmx.h v4.17
	id=13adefbe9e566c6db91579e4ce17f1e5193d6f2c
*/
#ifndef DMX_SET_SOURCE
typedef enum dmx_source {
	DMX_SOURCE_FRONT0 = 0,
	DMX_SOURCE_FRONT1,
	DMX_SOURCE_FRONT2,
	DMX_SOURCE_FRONT3,
	DMX_SOURCE_DVR0   = 16,
	DMX_SOURCE_DVR1,
	DMX_SOURCE_DVR2,
	DMX_SOURCE_DVR3
} dmx_source_t;
#define DMX_SET_SOURCE	_IOW('o', 49, dmx_source_t)
#endif
#endif

#include "../../common.h"

#include "../core/log.h"

#include "dvb.h"

void dvb_read (dvb_t *settings, bool(*data_callback)(int, unsigned char*))
{
	int cycles, total_size, fd;
	struct dmx_sct_filter_params params;
	dmx_source_t ssource;
	
	char first[settings->buffer_size];
	int first_length;
	bool first_ok;
	
	ssource = DMX_SOURCE_FRONT0 + settings->frontend;
	
	memset(&params, 0, sizeof(params));
	params.pid = settings->pid;
	params.filter.filter[0] = settings->filter[0];
	params.filter.mask[0] = settings->mask;
	params.timeout = 5000;
	params.flags = DMX_IMMEDIATE_START | DMX_CHECK_CRC;

	if ((fd = open(settings->demuxer, O_RDWR | O_NONBLOCK)) < 0) {
		log_add ("Cannot open demuxer '%s'", settings->demuxer);
		return;
	}

	if (ioctl(fd, DMX_SET_SOURCE, &ssource) == -1) {
		log_add ("ioctl DMX_SET_SOURCE failed");
		close(fd);
		return;
	}

	if (ioctl(fd, DMX_SET_FILTER, &params) == -1) {
		log_add ("ioctl DMX_SET_FILTER failed");
		close(fd);
		return;
	}

	log_add ("Reading pid 0x%x...", params.pid);

	first_length = 0;
	first_ok = false;
	total_size = 0;
	cycles = 0;
	while (cycles < MAX_OTV_LOOP_CYCLES)
	{
		//int k;
		//bool force_quit = false;
		unsigned char buf[settings->buffer_size];	// 4K buffer size
		int size = read (fd, buf, sizeof(buf));

		if (size == -1) {
			usleep (10 * 1000);
			continue;
		}

		if (size < settings->min_length) continue;
			
		if (first_length == 0)
		{
			first_length = size;
			memcpy (first, buf, size);
		}
		else if (first_length == size)
		{
			if (memcmp (buf, first, size) == 0) {
				first_ok = true;
			}
		}

		total_size += size;
		//data_callback (size, buf);
		if (!data_callback (size, buf)) {
			log_add ("Forced to quit");
			break;
		}

		if (first_ok) {
			log_add ("Done");
			break;
		}
		
		cycles++;
	}

	close(fd);
}
