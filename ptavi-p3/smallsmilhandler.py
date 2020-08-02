#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SmallSMILHandler(ContentHandler):

    def __init__(self):

        self.width = ""
        self.height = ""
        self.background_color = ""
        self.id = ""
        self.top = ""
        self.bottom = ""
        self.left = ""
        self.right = ""
        self.src = ""
        self.region = ""
        self.begin = ""
        self.dur = ""
        self.lista = []

    def startElement(self, etiqueta, atributo):
        if etiqueta == 'root-layout':
            self.widtch = atributo.get('width', "")
            self.height = atributo.get('height', "")
            self.background_color = atributo.get('background_color', "")
            self.lista.append({'etiqueta': etiqueta, 'width': self.width,
                               'height': self.height,
                               'background-color': self.background_color})
        elif etiqueta == 'region':
            self.id = atributo.get('id', "")
            self.top = atributo.get('top', "")
            self.bottom = atributo.get('bottom', "")
            self.left = atributo.get('left', "")
            self.right = atributo.get('right', "")
            self.lista.append({'etiqueta': etiqueta, 'id': self.id,
                               'top': self.top, 'bottom': self.bottom,
                               'left': self.left, 'right': self.right})
        elif etiqueta == 'img':
            self.src = atributo.get('src', "")
            self.region = atributo.get('region', "")
            self.begin = atributo.get('begin', "")
            self.dur = atributo.get('dur', "")
            self.lista.append({'etiqueta': etiqueta, 'src': self.src,
                               'region': self.region, 'begin': self.begin,
                               'dur': self.dur})
        elif etiqueta == 'audio':
            self.src = atributo.get('src', "")
            self.begin = atributo.get('begin', "")
            self.dur = atributo.get('dur', "")
            self.lista.append({'etiqueta': etiqueta, 'src': self.src,
                               'begin': self.begin, 'dur': self.dur})
        elif etiqueta == 'textstream':
            self.src = atributo.get('src', "")
            self.region = atributo.get('region', "")
            self.lista.append({'etiqueta': etiqueta, 'src': self.src,
                               'region': self.region})

    def get_tags(self):
        return self.lista


if __name__ == "__main__":
    """
    Programa principal
    """
    parser = make_parser()
    cHandler = SmallSMILHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))
    lista = cHandler.get_tags()
    print(lista)
