#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        print("La IP y el puerto del cliente es: " + str(self.client_address))
        while 1:
            line = self.rfile.read()
            if not line:
                break
            mensaje = line.decode("utf-8")
            print("El cliente nos manda " + mensaje)
            metodo = mensaje.split(" ")[0]
            if metodo == "INVITE":
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n"
                                 + b"SIP/2.0 180 Ringing\r\n\r\n"
                                 + b"SIP/2.0 200 OK\r\n\r\n")
            elif metodo == "ACK":
                Ejecutar = "mp32rtp -i 127.0.0.1 -p 23032  < " + AUDIO
                print("Vamos a ejecutar", Ejecutar)
                os.system(Ejecutar)

            elif metodo == "BYE":
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            elif metodo != ("INVITE", "ACK", "BYE"):
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")


if __name__ == "__main__":

    try:
        IP = sys.argv[1]
        PUERTOSER = int(sys.argv[2])
        AUDIO = sys.argv[3]
    except IndexError or ValueError:
        sys.exit("Usage: python server.py IP port audio_file")
    servidor = socketserver.UDPServer((IP, PUERTOSER), EchoHandler)
    print("Listening...")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor finalizado")
