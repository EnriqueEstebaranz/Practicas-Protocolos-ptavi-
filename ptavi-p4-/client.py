#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente UDP que abre un socket a un servidor
"""

import socket
import sys
"""
Constantes. Dirección IP del servidor y contenido a enviar
"""
SERVIDOR = sys.argv[1]
PUERTO = int(sys.argv[2])
LINEA = sys.argv[3:]
"""
Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
"""
try:
    SERVIDOR, PUERTO, METHOD, USUARIO, EXVAL = sys.argv[1:]
except ValueError:
    sys.exit("Debes escribir los siguientes datos: client.py servidor "
             "puerto register sip_address expires_value(int)")
REG = ("REGISTER sip:" + USUARIO + " SIP/2.0\r\nExpires: " + EXVAL + "\r\n\r\n")


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((SERVIDOR, int(PUERTO)))
    print("REGISTER sip:" + USUARIO + " SIP/2.0" + "\r\n")
    print("Expires: " + EXVAL + "\r\n\r\n")
    my_socket.send(bytes(REG, 'utf-8') + b'\r\n')

    try:
        data = my_socket.recv(1024).decode('utf-8')
    except ConnectionRefusedError:
        sys.exit("Nó se establecio conexion al servidor")
    print(data)
