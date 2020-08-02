#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Server del UA
"""
import sys
import os
import socketserver
from uaclient import XmlHandler, log
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


try:
    CONFIG = sys.argv[1] # ficheroxml con los parametros de configuración.
except IndexError or ValueError or TypeError:
    sys.exit("Usage: python uaserver.py config")


class HandlerEchoServer(socketserver.DatagramRequestHandler):

    def handle(self):

        solicitud = self.rfile.read().decode("utf-8")
        metodo = solicitud.split()[0]
        start = ("Start server")
        log(start, LOG_PATH)
        solicitud_log = solicitud.replace("\r\n", " ")
        log("Received from: " + PROXY_IP + ":" + PROXY_PUERTO + ": " +
            solicitud_log, LOG_PATH)
        if metodo == "INVITE":
            line = ("SIP/2.0 100 Trying\r\n\r\n" +
                    "SIP/2.0 180 Ringing\r\n\r\n" +
                    "SIP/2.0 200 OK\r\n" +
                    "Content-Type: application/sdp\r\n\r\n" +
                    "v=0\r\n" + "o=" + USERNAME + " " + IP_UASERVER + "\r\n "
                    + "s=misesion\r\n" + "m=audio " + str(RTPAUDIO) +
                    " RTP  \r\n\r\n")
            self.wfile.write(bytes(line, 'utf-8')+ b'\r\n')
            log("Sent to" + PROXY_IP + ":" + PROXY_PUERTO + ": " + line,
                LOG_PATH)
        elif metodo == "ACK":
            aEjecutar  = "./mp32rtp -i " + IP_UASERVER + " -p " + str(RTPAUDIO)
            aEjecutar += " < " + AUDIO_PATH
            print("Vamos a ejecutar", aEjecutar )
            os.system(aEjecutar)
            log("Sent to" + PROXY_IP + ":" + PROXY_PUERTO + ": " + aEjecutar ,
                LOG_PATH)
        elif metodo == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK:\r\n\r\n")
            line = ("SIP/2.0 200 OK:")
            log("Sent to" + PROXY_IP + ":" + PROXY_PUERTO + ": " + line,
                LOG_PATH)
        elif metodo != ("INVITE", "ACK", "BYE"):
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed:\r\n\r\n")
            line = "SIP/2.0 405 Method Not Allowed:\r\n\r\n"
            log(line, LOG_PATH)
            print("Metodo erroneo ):")
            print(solicitud)
        else:
            self.wfile.write(b"SIP/2.0 400 Bad Request...\r\n\r\n")
            line = ("Error: SIP/2.0 400 Bad Request...")
            log(line, LOG_PATH)


if __name__ == "__main__":

    parser = make_parser()
    myHandler = XmlHandler()
    parser.setContentHandler(myHandler)
    try:
        parser.parse(open(CONFIG))
    except FileNotFoundError:
        sys.exit("Usage: python uaserver.py config")
    CONFIGXML = myHandler.get_tags()
    # Pasamos los datos leidos xml a constantes
    USERNAME = CONFIGXML["account_username"]
    PASSWORD = CONFIGXML["account_passwd"]
    IP_UASERVER = CONFIGXML["uaserver_ip"]
    PUERTO_UASERVER = int(CONFIGXML["uaserver_puerto"])
    RTPAUDIO = int(CONFIGXML["rtpaudio_puerto"])
    PROXY_IP = CONFIGXML["regproxy_ip"]
    PROXY_PUERTO = CONFIGXML["regproxy_puerto"]
    LOG_PATH = CONFIGXML["log_path"]
    AUDIO_PATH = CONFIGXML["audio_path"]

    serv = socketserver.UDPServer((IP_UASERVER, PUERTO_UASERVER), HandlerEchoServer)
    print("Listening:\r\n")
    log("start:", LOG_PATH)

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Server interrumpido")
        log("Finish", LOG_PATH)
