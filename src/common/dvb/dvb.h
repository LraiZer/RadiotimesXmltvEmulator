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
	char		*demuxer;
	int		frontend;
	unsigned int	min_length;
	unsigned int	buffer_size;
	unsigned char	filter[DMX_FILTER_SIZE];
	unsigned char	mask;
} dvb_t;

void dvb_read (dvb_t *settings, bool(*data_callback)(int, unsigned char*));

#endif // _DVB_H_
