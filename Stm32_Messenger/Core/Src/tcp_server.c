/*
 * tcp_server.c
 *
 *  Created on: Mar 29, 2022
 *      Author: Rzeszutko
 */

#include "FreeRTOS.h"
#include "cmsis_os2.h"
#include "tcp_server.h"
#include "task.h"
#include "lwip.h"
#include "main.h"
#include "sys_arch.h"
#include "usart.h"
#include "printf.h"

#include <stdint.h>


/* DEFINE SECTION */

/* TCP CONFIGURATION */
#define FIRST_PORT 				7U
#define SECOND_PORT 			8U

#define BACKLOG_CONNECTION		1U

/* THREADS CONFIGURATION */
#define THREAD_STACK_SIZE		(DEFAULT_THREAD_STACKSIZE * 2U)

/* BUFFER SIZE */
#define MSG_BUFFER_SIZE 		128

#define IP_ADDRESS_LENGTH		14U

#define CLIENT_EXIST(client)	(client.id > 0)


/* Local object definition */
static socket_t First, Second;

/* Local function definition */
static void FirstClient(void *args);
static void SecondClient(void *args);
static char * get_ip_address(const struct in_addr *address);


/* FUCTNIONS */

void tcp_server_init(void)
{
	/* Create two threads to handle the connection */
	sys_thread_new("FirstClient", FirstClient, NULL, THREAD_STACK_SIZE, osPriorityHigh);
	sys_thread_new("SecondClient", SecondClient, NULL, THREAD_STACK_SIZE, osPriorityHigh);
}


static socket_t tcp_create_socket(uint16_t port)
{
	socket_t Socket = {0};
	struct sockaddr_in address, host;
	socket_id client;

	client = lwip_socket(AF_INET, SOCK_STREAM, 0);

	if(client < 0)
		return Socket;

	address.sin_family = AF_INET;
	address.sin_port = htons(port);
	address.sin_addr.s_addr = INADDR_ANY;

	if(0 > lwip_bind(client, (struct sockaddr*)&address, sizeof(address)))
		return Socket;


	lwip_listen(client, BACKLOG_CONNECTION);

	size_t size = sizeof(host);

	Socket.id = lwip_accept(client, (struct sockaddr *)&host, (socklen_t *)&size);

	memcpy(&Socket.host_adr, &host, sizeof(host));

	printf("Client: %s connected to port: %u\n\r", get_ip_address(&Socket.host_adr.sin_addr), port);

	return Socket;
}

static void FirstClient(void *args)
{
	static uint8_t msg_buf[MSG_BUFFER_SIZE];

	First = tcp_create_socket(FIRST_PORT);

	int data_length = 0;

	while(1)
	{
		if(CLIENT_EXIST(First))
		{
			data_length = lwip_read(First.id, msg_buf, MSG_BUFFER_SIZE);

		    if(data_length > 0)
		    {
		    	printf("From %s received: %s\n\r", get_ip_address(&First.host_adr.sin_addr), msg_buf);
			    lwip_write(Second.id, (uint8_t*)msg_buf, sizeof(msg_buf));
			    memset(msg_buf, 0, MSG_BUFFER_SIZE);
		    }

			if(data_length < 0)
			{
				printf("First client disconnected\n\r");
				osThreadTerminate(osThreadGetId());
			}
		}
		else
		{
			printf("Error during creating connection\n\r");
			osThreadTerminate(osThreadGetId());
		}
	}
}


static void SecondClient(void *args)
{
	static uint8_t msg_buf[MSG_BUFFER_SIZE];

	Second = tcp_create_socket(SECOND_PORT);
	int data_length = 0;

	while(1)
	{
		if(CLIENT_EXIST(Second))
		{
			data_length = lwip_read(Second.id, msg_buf, MSG_BUFFER_SIZE);

			if(data_length >= 0)
		    {
		    	printf("From %s received: %s\n\r", get_ip_address(&Second.host_adr.sin_addr), msg_buf);
			    lwip_write(First.id, (uint8_t*)msg_buf, sizeof(msg_buf));
			    memset(msg_buf, 0, MSG_BUFFER_SIZE);
		    }

			if(data_length < 0)
			{
				printf("Second client disconnected\n\r");
				osThreadTerminate(osThreadGetId());
			}
		}
		else
		{
			printf("Error during creating connection\n\r");
			osThreadTerminate(osThreadGetId());
		}
	}
}


static char * get_ip_address(const struct in_addr *address)
{
	static char ip_address[IP_ADDRESS_LENGTH];
	uint32_t value = address->s_addr;

	(void)sprintf(ip_address, "%u.%u.%u.%u", (value & 0x000000FF),
											 (value & 0x0000FF00) >> 8,
											 (value & 0x00FF0000) >> 16,
											 (value & 0xFF000000) >> 24);

	return ip_address;
}
