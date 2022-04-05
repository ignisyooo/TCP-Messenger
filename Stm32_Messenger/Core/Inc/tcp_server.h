/*
 * tcp_server.h
 *
 *  Created on: Mar 29, 2022
 *      Author: Rzeszutko
 */

#ifndef INC_TCP_SERVER_H_
#define INC_TCP_SERVER_H_

#include "sockets.h"


typedef int socket_id;
typedef struct sockaddr_in host_address_t;

typedef struct
{
	socket_id	id;
	host_address_t host_adr;
} socket_t;

void tcp_server_init(void);


#endif /* INC_TCP_SERVER_H_ */
