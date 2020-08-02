#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de SIP en UDP simple
"""

import socketserver
import sys
import time
import json


class SIPRegistrerHandler(socketserver.DatagramRequestHandler):
    """SIP server class"""

    def handle(self):

        """handle de la clase"""
        while 1:
            line = self.rfile.read()
            line_client = line.decode('utf-8').split()
            if not line:
                break  # Fin del bucle
            else:
                print("Petición recibida \r\n")

            if line_client[0] == 'REGISTER':
                # Guardamos dirección del servidor en nuestro diccionario.
                direccion = line_client[1].split(':')
                usuario = direccion[1]
                expires = int(line_client[4])
                time_actual = int(time.time())
                time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                                time.gmtime(time_actual))
                time_exp = int(expires + time_actual)
                time_exp_string = time.strftime('%Y-%m-%d %H:%M:%S',
                                                time.gmtime(time_exp))
                self.lista = []
                dicc[usuario] = [self.client_address[0], time_exp_string]
                self.lista.append(dicc)
                print("SIP/2.0 200 OK\r\n")
                self.wfile.write(b"SIP/2.0 200 OK" + b'\r\n\r\n')
                if line_client[4] == '0':
                    print("Lo borramos del diccionario")
                    del dicc[usuario]
                    print(self.lista)
                else:
                    print(self.lista)
        self.register2json()

    def register2json(self):
        with open('registered.json', 'w') as archivo_json:
            json.dump(self.lista, archivo_json, sort_keys=True,
                      indent=4, separators=(',', ':'))
    def json2registered(self):
        try:
            with open('registered.json', 'r') as archivo_json:
                self.lista = json.load(self.lista)
        except:
            pass


if __name__ == "__main__":

    dicc = {}
    try:
        PORT = int(sys.argv[1])
    except IndexError:
        sys.exit("Debe introducir: server.py port_number")
    """Creamos UDP en el puerto que indicamos utilizando la clase."""
    serv = socketserver.UDPServer(('', PORT), SIPRegistrerHandler)
    print("Iniciando servidor... \r\n")
    try:
        """Creamos el servidor"""
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Fin del servidor")
