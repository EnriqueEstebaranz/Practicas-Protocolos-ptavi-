#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Proxy Registrar
"""
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import socketserver
import time
import json
import random
import hashlib
from uaclient import log
from uaclient import defpassword

try:
    CONFIG = sys.argv[1]
except IndexError or ValueError or TypeError:
    sys.exit("Usage: python proxy_registrar.py config")



class proxyRHandler(ContentHandler):

    def __init__(self):

        self.lista = {}
        self.diccionarioproxy = {
                                 "server"  : ["name", "ip", "puerto"],
                                 "database":   ["path", "passwdpath"],
                                 "log"     :                 ["path"]}

    def startElement(self, name, attrs):
        dicc = {}
        if name in self.diccionarioproxy:
            for atributo in self.diccionarioproxy[name]:
                self.lista[name + "_" + atributo] = attrs.get(atributo, "")

    def get_tags(self):
        return self.lista

class SIPRegisterHandler(socketserver.DatagramRequestHandler):

    registrar = {}
    nonce = {}
    dicc_password = {}

    def registrarajson(self):
        """
        Escribe el diccionario en el formato json en registered.json.
        """
        with open("basededatos.json", "w") as jsonfile:
            json.dump(self.registrar, jsonfile, indent=4)


    def jsonaregistrar(self):
        """Descargo fichero json en el diccionario."""
        try:
            with open("basededatos.json", 'r') as jsonfile:
                self.registrar = json.load(jsonfile)
        except:
            pass


    def registro(self, users, puerto, expire):
        self.jsonaregistrar()
        self.registrar[users] = {'ip': self.client_address[0],
                                 'puerto': puerto,
                                 'expires': expire}


    def jsonapasswd(self):
        """
        Se descarga json en el diccionario.
        """
        try:
            with open(DATABASE_PASSWD, 'r') as jsonfile:
                self.dicc_password = json.load(jsonfile)
        except (FileNotFoundError, ValueError):
            pass


    #def senttoserver(self, ipcliente, puertocliente, metodo, mensaje):
        #"""Envio al servidor."""
        #with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        #    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #    my_socket.connect((ipcliente, int(puertocliente)))
        #    mensaje_proxy = ("Envio el metodo " + metodo + "al server:\r\n" +
        #                     mensaje)
        #    print(mensaje_proxy)
        #    my_socket.send(bytes(mensaje_proxy, 'utf-8') + b'\r\n\r\n')
        #    mensaje_proxy = mensaje_proxy.replace("\r\n", " ")
        #    log("sent to " + ipcliente + ":" + str(puertocliente) + ":" +
        #        mensaje_proxy, LOG_PATH)
        #    try:
        #        data = my_socket.recv(1024).decode('utf-8')
        #        print("Recibo del servidor: " + data)
        #        data = data.replace("\r\n", " ")
        #        log("Received from" + ipcliente + ":" + str(puertocliente) + ":"
        #             + data, LOG_PATH)
        #    except ConnectionRefusedError:
        #        log("Error: No server listening: " + ipcliente + "puerto" +
        #            str(puertocliente), LOG_PATH)


    def handle(self):

        solicitud = self.rfile.read().decode("utf-8")
        forma = ("Via: SIP/2.0/UDP " + IP + ":" + str(PUERTO_SERVER) +  "\r\n")
        peticion = solicitud + forma
        print("El cliente manda:\r\n" + peticion)
        ipcliente = str(self.client_address[0])
        puertocliente = str(self.client_address[1])
        metodo = solicitud.split()[0]
        user = solicitud.split()[1].split(":")[1]
        solicitud_log = solicitud.replace("\r\n", " ")
        log("Received from" + ipcliente + ":" + puertocliente + ": " +
            solicitud_log, LOG_PATH)
        metodo = solicitud.split()[0]
        self.jsonapasswd()
        self.jsonaregistrar()
        if metodo == "REGISTER" :
            print(solicitud)
            user = solicitud.split()[1].split(":")[1]
            userport = solicitud.split()[1].split(":")[2]
            expires = solicitud.split()[4]
            puertocliente = str(self.client_address[1])
            ipcliente = str(self.client_address[0])
            expires_time = int(expires) + time.time()
            act_time = time.time()

            if metodo == "REGISTER" and len(solicitud.split()) == 5: # Si es 5 es el  primer register.
                if user not in self.registrar:
                    self.nonce[user] = str(random.randint(0, 99999999))
                    LINE = ("SIP/2.0 401 Unauthorized\r\n" +
                            'WWW Authenticate: Digest nonce="' +
                            self.nonce[user] + '"\r\n\r\n')
                    print("Enviando al cliente: \r\n" + LINE)

                else:
                    LINE = ("SIP/2.0 200 OK" + "\r\n\r\n")
                    if expires == "0":
                        log('Send: ' + user + ':' + userport +
                            ': SIP/2.0 200 OK. Deleting.\r\n', LOG_PATH)
                        del self.registrar[user] #deja de estar registrado
                self.wfile.write(bytes(LINE, "utf-8"))
                log("Sent to" + ipcliente + ":" + puertocliente + ": " + LINE,
                    LOG_PATH)
            elif metodo == "REGISTER" and len(solicitud.split()) != 5:

                contrasena = self.dicc_password[user]["passwd"]
                variable = hashlib.md5()
                variable.update(bytes(contrasena, 'utf-8'))
                variable.update(bytes(self.nonce[user], 'utf-8'))
                nonce_recv = solicitud.split()[8].split('"')[1]
                if variable.hexdigest() == nonce_recv:
                    print("contraseña correcta")
                    LINE = ("SIP/2.0 200 OK" + "\r\n\r\n")
                    self.registro(user, userport, expires)
                else:
                    LINE = ("ERROR: Clave no valida")
            else:
                LINE = ("SIP/2.0 404 User not found" + "\r\n\r\n")

            self.wfile.write(bytes(LINE, 'utf-8'))
            log("sent to" + ipcliente + puertocliente + LINE, LOG_PATH)
            self.registrarajson()

        elif metodo == "INVITE":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                user = solicitud.split()[1].split(":")[1]
                self.jsonaregistrar()
                if user in self.registrar:
                    print(self.registrar[user]["puerto"])
                    print(self.registrar[user]["ip"])
                    try:
                        ipuser = self.registrar[user]["ip"]
                        puerto = self.registrar[user]["puerto"]
                        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        my_socket.connect((ipuser, int(puerto)))
                        my_socket.send(bytes(solicitud, 'utf-8')+ b'\r\n\r\n')
                        data = my_socket.recv(1024).decode('utf-8')
                        self.wfile.write(bytes(data, 'utf-8'))
                        print("Recibo del servidor: " + data)
                    except (ConnectionRefusedError, KeyError):
                        recv = ""
                        self.wfile.write(bytes("SIP/2.0 400 Bad Request\r\n\r\n",
                                               'utf-8'))
                else:
                    LINE = ("SIP/2.0 404 User not found" + "\r\n\r\n")
                    self.wfile.write(bytes(LINE, 'utf-8'))
                    log("Error: User not found", LOG_PATH)
                    self.registrarajson()


        elif metodo == "BYE":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                print(solicitud)
                user = solicitud.split()[1].split(":")[1]
                ipuser = self.registrar[user]["ip"]
                puerto = self.registrar[user]["puerto"]
                line = solicitud.replace("\r\n", " ")
                log("Recieved from " + ipuser + ":" + puerto + ":" +
                line, LOG_PATH)
                if user in self.registrar:
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ipuser, int(puerto)))
                    my_socket.send(bytes(solicitud, 'utf-8')+ b'\r\n\r\n')
                    data = my_socket.recv(1024).decode('utf-8')
                    self.wfile.write(bytes(data, 'utf-8'))
                    print("Recibo del servidor: " + data)
                    data = data.replace("\r\n", " ")
                    log("Sent to" + ipuser + ":" + puerto + ": " +
                        data, LOG_PATH)
                else:
                    mensaje = ("SIP/2.0 404 User not found \r\n\r\n")
                    self.wfile.write(bytes(mensaje, 'utf-8'))
                    linea = ("Error: SIP/2.0 404 User not found:")
                    log(linea, LOG_PATH)
                self.registrarajson()
        elif metodo == "ACK":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                print(solicitud)
                #recibe ACK sip:chocapicduo@ptavi.es SIP/2.0
                user = solicitud.split()[1].split(":")[1]
                ipuser = self.registrar[user]["ip"]
                puerto = self.registrar[user]["puerto"]
                line = solicitud.replace("\r\n", " ")
                log("Recieved from " + ipuser + ":" + puerto + ":" +
                line, LOG_PATH)
                if user in self.registrar:
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ipuser, int(puerto)))
                    my_socket.send(bytes(solicitud, 'utf-8')+ b'\r\n\r\n')
                    data = my_socket.recv(1024).decode('utf-8')
                    self.wfile.write(bytes(data, 'utf-8'))
                    print("Recibo del servidor: " + data)
                else:
                    mensaje = ("SIP/2.0 404 User not found \r\n\r\n")
                    self.wfile.write(bytes(mensaje, 'utf-8'))
                    linea = ("Error: SIP/2.0 404 User not found:")
                    log(linea, LOG_PATH)
                self.registrarajson()


        elif metodo != ("REGISTER", "INVITE", "ACK", "BYE"):
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            mensajelog = ("Error: SIP/2.0 405 Method Not Allowed")
            log(mensajelog, LOG_PATH)
            print("Error por metodo")
        else:
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            mensajelog = ("Error: SIP/2.0 400 Bad Request")
            log(mensajelog, LOG_PATH)
        self.registrarajson()
        mensajefinlog = ("Finish")
        log(mensajefinlog, LOG_PATH)

if __name__ == "__main__":

    parser = make_parser()
    prHandler = proxyRHandler()
    parser.setContentHandler(prHandler)
    try:
        parser.parse(open(CONFIG))
    except FileNotFoundError:
        sys.exit("Usage: python proxy_registrar.py config")
    CONFIGXML = prHandler.get_tags()

    IP = CONFIGXML["server_ip"]
    PUERTO_SERVER = int(CONFIGXML["server_puerto"])
    USERNAME = CONFIGXML["server_name"]
    LOG_PATH = CONFIGXML["log_path"]
    DATABASE_PATH = CONFIGXML["database_path"]
    DATABASE_PASSWD = CONFIGXML["database_passwdpath"]

    serv = socketserver.UDPServer((IP, PUERTO_SERVER), SIPRegisterHandler)
    print("Server " + USERNAME + " listening at port " + str(PUERTO_SERVER))
    log("Starting...", LOG_PATH)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        sys.exit("\r\n Proxy finalizado")
        log("Finishing.", LOG_PATH)
