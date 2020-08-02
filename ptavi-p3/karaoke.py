#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import smallsmilhandler
import urllib.request
import json
from xml.sax import make_parser


class Karaokelocal:

    def __init__(self, fichero):
        try:
            fichero = sys.argv[1]
            parser = make_parser()
            cHandler = smallsmilhandler.SmallSMILHandler()
            parser.setContentHandler(cHandler)
            parser.parse(open(fichero))
            self.lista = cHandler.get_tags()
        except FileNotFoundError:
            sys.exit('file not found')
            """
            abrimos ficheros y creamos la clase
            karaokelocal heredando el programa
            SmallSMILHandlerrealizado anteriormente
            """

    def __str__(self):
        """
        ordena y coloca lo que tenemos en karaoke.smil
        para que salga de salida lo que nos pide
        """
        line = ''
        for linea in self.lista:
            for atributo in linea:
                if linea[atributo] != "":
                    line += atributo + "=" + "'" + linea[atributo] + "'" + '\t'
            line += '\n'
        return line

    def to_json(self, smil):
        ficherojs = ''
        if ficherojs == '':
            ficherojs = smil.replace('.smil', '.json')

        with open(ficherojs, 'w') as filejson:
            json.dump(self.lista, filejson, indent=4)

    def do_local(self):

        for linea in self.lista:
            for atributo in linea:
                if linea[atributo][0:7] == 'http://':
                    direction = linea[atributo].split('/')[-1]
                    urllib.request.urlretrieve(linea[atributo])
                    linea[atributo] = direction
        """
        modifica el valor del atributo correspondiente,indicando
        ahora  su  localizacion  local
        """


if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        fichero = sys.argv[1]
        karaoke = Karaokelocal(fichero)
    except():
        sys.exit('usage error: python3 karaoke.py file smil')
    print(karaoke)
    karaoke.to_json(fichero)
    karaoke.do_local()
    karaoke.to_json('local.smil')
    print(karaoke)
