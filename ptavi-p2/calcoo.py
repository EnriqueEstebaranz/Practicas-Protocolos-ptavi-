#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys


class Calculadora():

    "Esto la clase calculadora"

    def init(self, operando1, operando2):

        self.operando1 = operando1
        self.operando2 = operando2

    def suma(self):

        "Esto es la función suma"

        return self.operando1 + self.operando2

    def resta(self):

        "Esto es la función resta"

        return self.operando1 - self.operando2


if __name__ == "__main__":

    try:

        operando1 = int(sys.argv[1])
        operando2 = int(sys.argv[3])

    except ValueError:
        sys.exit("Error: Non numerical parameters")

    "Se comprueba que los valores del operando1 y operando2 son enteros"

    calcu = Calculadora()
    calcu.init(operando1, operando2)
    if sys.argv[2] == "suma":
        result = calcu.suma()
    elif sys.argv[2] == "resta":
        result = calcu.resta()
    else:
        sys.exit('Operación sólo puede ser sumar o restar.')

    "se ejecuta la función suma y resta y comprueba que el operando es valido"

    print(result)

    "imprime el resultado"
