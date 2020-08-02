#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys


# Cliente UDP simple.
try:
    # Metodo será un metodo SIP.
    METODO = sys.argv[1]
    # Login mas la ip del servidor(el split permite dividir en dos el argv[2]).
    RECEPTOR_IP = sys.argv[2].split(":")[0]
    # Dirección IP del servidor.
    IPSERVIDOR = RECEPTOR_IP.split("@")[1]
    # Puerto al que se dirige el mensaje.
    PUERTO = int(sys.argv[2].split(":")[1])


# En caso de no introducir el numero de parámetros correctos o de error.
except IndexError or ValueError:
    sys.exit("Usage: python3 client.py method receiver@IP:SIPport")

cliente = (METODO + " sip:" + RECEPTOR_IP + " SIP/2.0")
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((IPSERVIDOR, int(PUERTO)))
    print("Enviando: " + cliente)
    my_socket.send(bytes(cliente, "utf-8") + b"\r\n\r\n")
    try:
        data = my_socket.recv(1024)
    except ConnectionRefusedError:
        sys.exit("No se pudo establecer conexión porque la máquina de destino",
                 " lo rechazó activamente")
    CodigoRespuesta = data.decode("utf-8")
    print("Recibido --", CodigoRespuesta)
    CodigoRespuesta = CodigoRespuesta.split()

    if METODO == "INVITE":
        triying = CodigoRespuesta[2]
        ringing = CodigoRespuesta[5]
        ok = CodigoRespuesta[8]
        if triying == "Trying" and ringing == "Ringing" and ok == "OK":
            my_socket.send(bytes('ACK sip:' + RECEPTOR_IP + ' SIP/2.0',
                                 'utf-8') + b'\r\n\r\n')
    if METODO == "BYE":
        if data.decode("utf-8") == "SIP/2.0 200 OK\r\n\r\n":
            print("Terminando socket...")
