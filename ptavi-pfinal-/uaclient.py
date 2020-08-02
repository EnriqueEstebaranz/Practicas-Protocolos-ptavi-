#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Cliente del UA
"""

import sys
import socket
import time
import hashlib
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XmlHandler(ContentHandler):

    def __init__(self):
        """Inicializa el diccionario con los datos del XML"""
        self.lista = {}
        self.diccionario_xml = {
                            "account" : ["username", "passwd"],
                            "uaserver":       ["ip", "puerto"],
                            "rtpaudio":             ["puerto"],
                            "regproxy":       ["ip", "puerto"],
                            "log"     :               ["path"],
                            "audio"   :               ["path"]}

    def startElement(self, name, attrs):
        """Se genera un diccionario con los valores de los ficheros ua1/ua2"""
        if name in self.diccionario_xml:
            for atributo in self.diccionario_xml[name]:
                self.lista[name + "_" + atributo] = attrs.get(atributo, "")

    def get_tags(self):
        """Diccionario"""
        return self.lista


def log(mensaje, log_path):
    """Abre un fichero log para indicar la ruta de registro, etc."""
    fich = open(log_path, "a")
    fich.write(time.strftime('%Y%m%d%H%M%S '))
    fich.write(mensaje + "\r\n")
    fich.close()


def defpassword(passwd, nonc):
    """Devuelve el nonce de respuesta."""
    encriptado = hashlib.md5()
    encriptado.update(bytes(passwd, 'utf-8'))
    encriptado.update(bytes(str(nonc),  'utf-8'))
    return encriptado.hexdigest()


def errores(respuesta):
    if "400" in data:
        respuesta = (" Error: SIP/2.0 400 Bad Request:")
        log("Error: " + data, LOG_PATH)
        print(respuesta)
    elif "404" in data:
        respuesta = (" Error: SIP/2.0 404 User not found:")
        log("Error: " + data, LOG_PATH)
        print(respuesta)
    elif "405" in data:
        respuesta = (" Error: SIP/2.0 405 Method Not Allowed:")
        log("Error: " + data, LOG_PATH)
        print(respuesta)


def enviortp (ip, puerto, audio):
    aejecutar = "mp32rtp -i " + ip + " -p " + puerto + " < " + audio
    return aejecutar


if __name__ == "__main__":

    # Cliente UDP simple.
    try:
        # Config sera un fichero xml con la configuración.
        CONFIG = sys.argv[1]
        # Metodo será un metodo SIP.
        METODO = sys.argv[2]
        # Opcion sera un parametro opcional dependiendo del metodo utilizado.
        OPCION = sys.argv[3]

    except IndexError or ValueError or TypeError:
        sys.exit("Usage: python uaclient.py config method option")

    parser = make_parser()
    MyHandler = XmlHandler()
    parser.setContentHandler(MyHandler)
    try:
        parser.parse(open(CONFIG))
    except FileNotFoundError:
        sys.exit("Usage: python uaclient.py config method option")
    configxml = MyHandler.get_tags()
    # Pasamos los datos leidos xml a constantes
    USERNAME        =    configxml["account_username"]
    PASSWORD        =      configxml["account_passwd"]
    # Opcional (en caso de no estar indicada se usa 127.0.0.1).
    if configxml["uaserver_ip"] == " ":
        IP_UASERVER = "127.0.0.1"
    else:
        IP_UASERVER =         configxml["uaserver_ip"]
    PUERTO_UASERVER = int(configxml["uaserver_puerto"])
    RTPAUDIO        = int(configxml["rtpaudio_puerto"])
    PROXY_IP        =         configxml["regproxy_ip"]
    PROXY_PUERTO    =     configxml["regproxy_puerto"]
    LOG_PATH        =            configxml["log_path"]
    AUDIO_PATH      =          configxml["audio_path"]
    # Creamos el socket, lo configuramos y lo atamos a un ip/puerto del proxy.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((PROXY_IP, int(PROXY_PUERTO)))
        log("Starting...", LOG_PATH)

        if METODO == "REGISTER":
            LINE = (METODO + " sip:" + USERNAME + ":" + str(PUERTO_UASERVER) +
                    " SIP/2.0\r\n" + "Expires: " + OPCION + "\r\n\r\n")
            print('Enviando Register al proxy_registrar: ' + '\r\n' + LINE )
            my_socket.send(bytes(LINE, 'utf-8') )
            LINE = LINE.replace("\r\n", " ")
            log("sent to " + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " + LINE,
                 LOG_PATH)
            data = my_socket.recv(1024).decode("utf-8")
            print("Recibo del proxy_registrar:" + "\r\n", data)
            data = data.replace("\r\n", " ")
            log("Received from " + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " +
                data, LOG_PATH)
            if "401" in data:
                variable = hashlib.md5()
                NONCE_RECV = data.split()[6].split('"')[1]
                print(NONCE_RECV)
                variable.update(bytes(PASSWORD, 'utf-8'))
                variable.update(bytes(NONCE_RECV, 'utf-8'))

                LINE = (METODO + " sip:" + USERNAME + ":" +
                        str(PUERTO_UASERVER) + " SIP/2.0" + "\r\n" +"Expires: "
                        + OPCION + "\r\n" + 'Authorization: Digest response ="'
                        + variable.hexdigest() + '"' + "\r\n\r\n")
                print("Enviamos al Proxy:" + "\r\n", LINE)
                my_socket.send(bytes(LINE, "utf-8")+ b'\r\n')
                LINEA = LINE.split('\r\n')
                datos = " ".join(LINEA)
                log("Sent to " + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " +
                    datos, LOG_PATH)
                data = my_socket.recv(1024).decode('utf-8')
                print("Recibido: " + "\r\n", data)

            else:
                errores(data)
        elif METODO == "INVITE":
            LINE =(METODO + " sip:" + OPCION + " SIP/2.0\r\n" +
                   "Content-Type: application/sdp \r\n\r\n v=0" + "\r\n o=" +
                   USERNAME + " " + IP_UASERVER + "\r\n" + " s=SesiondeEnrique"
                   + "\r\n t=0 \r\n m=audio" + str(RTPAUDIO) + " RTP \r\n\r\n")
            print("Enviando Invite al proxy_registrar: " + "\r\n" + LINE)
            my_socket.send(bytes(LINE, 'utf-8'))
            LINE = LINE.replace("\r\n", " ")
            log("Sent to " + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " + LINE,
                        LOG_PATH)
            data = my_socket.recv(1024).decode('utf-8')
            print("Recibo del proxy_registrar:" + "\r\n" + data)
            data = data.replace("\r\n", " ")
            log("Received from " + PROXY_IP + ":" + PROXY_PUERTO + ":" + data,
                LOG_PATH)
            if "100" in data:
                print(data)
                data_lista = data.split()
                IP = data_lista[13]
                RTPUERTO = data_lista[16]
                print(IP)
                print(RTPUERTO)
                LINE = ("ACK sip:" + OPCION + " SIP/2.0" + "\r\n\r\n")
                print("Enviando ACK al proxy-registrar:" + '\r\n' + LINE)
                my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                LINE = LINE.replace("\r\n", " ")
                log("Sent to " + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " +
                    LINE, LOG_PATH)
                LINE = enviortp(IP, RTPUERTO, AUDIO_PATH)
                log("Sent to " + IP + ":" + RTPUERTO + ": " +
                    LINE, LOG_PATH)
                data = my_socket.recv(1024).decode("utf-8")
                print("Recibo del proxy_registrar:" + "\r\n" + data)
                data = data.replace("\r\n", " ")
                log("Received from " + PROXY_IP + ":" + PROXY_PUERTO + ":" +
                    data, LOG_PATH)
            else:
                errores(data)
                print("error")
        elif METODO == "BYE":
            LINE = (METODO + " sip:" + OPCION + " SIP/2.0\r\n")
            print("Enviando BYE al proxy-registrar:" + '\r\n' + LINE)
            my_socket.send(bytes(LINE, "utf-8") + b'\r\n')
            LINE = LINE.replace("\r\n", " ")
            log("Sent to" + PROXY_IP + ":" + str(PROXY_PUERTO) + ": " +
                LINE, LOG_PATH)
            data = my_socket.recv(1024).decode("utf-8")
            print("Recibo del proxy_registrar:" + "\r\n" + data)
            if "200" in data:
                data = data.replace("\r\n", " ")
                log("Received from " + PROXY_IP + ":" + PROXY_PUERTO + ":" +
                    data, LOG_PATH)
            else:
                errores(data)
        else:
            LINE = (METODO + " sip:" + OPCION + " SIP/2.0\r\n")
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024).decode('utf-8')
            print("Recibo del proxy_registrar:" + "\r\n" + data)
            print(data)
            errores(data)
            print("Metodo mal escrito,(REGISTER, INVITE y BYE)")

        print("fin")
        log('Finishing.', LOG_PATH)
