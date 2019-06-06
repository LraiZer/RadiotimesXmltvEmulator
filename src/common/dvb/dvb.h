#ifndef _DVB_H_
#define _DVB_H_

typedef struct buffer_s
{
	unsigned short	size;
	unsigned char	*data;
} buffer_t;

typedef struct dvb_s
{
	int		pid;
	int		*pids;
	char		*demuxer;
	int		frontend;
	unsigned int	pids_count;
	unsigned int	min_length;
	unsigned int	buffer_size;
	unsigned char	filter;
	unsigned char	mask;
} dvb_t;

void dvb_read (dvb_t *settings, bool(*data_callback)(int, unsigned char*));

#endif // _DVB_H_
