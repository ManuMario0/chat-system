import socket
import threading
import os
import errno
import fcntl
from time import sleep
import sys

semaphore = threading.Semaphore()
chat = []

def instanceServer (socket_client, address_client):
    print("Client connected. Addr " + str(address_client[0]) + " port : " + str(address_client[1]))
    fin = False
    pseudo = ""
    index = 0
    fcntl.fcntl(socket_client, fcntl.F_SETFL, os.O_NONBLOCK)
    while (not fin):
        string_to_send = ""
        semaphore.acquire()
        for m in chat[index:]:
            string_to_send += m[0] + " : " + m[1]
        index = len(chat)
        semaphore.release()
        if len(string_to_send) > 0:
            socket_client.send(string_to_send.encode("utf-8"))
        try:
            data_recv_from_client = socket_client.recv(4096)
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                sleep(1)
                continue
            else:
                # a "real" error occurred
                print(e)
                sys.exit(1)
        else:
            data = data_recv_from_client.decode("utf-8")
            print(data_recv_from_client.decode("utf-8"))
            if data[0] == 'P':
                pseudo = data[1:-2]
            elif data[0] == 'D':
                semaphore.acquire()
                chat.append([pseudo, str(data[1:])])
                semaphore.release()
            else:
                fin = True
    print("Connection closed with " + address_client[0] + ":" + str(address_client[1]))
    socket_client.close()

address_socket = ("", 8081)
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind(address_socket)
socket_server.listen()

while True:
  socket_created_for_client, address_client = socket_server.accept()
  threading._start_new_thread(instanceServer, (socket_created_for_client, address_client))

socket_server.close()
