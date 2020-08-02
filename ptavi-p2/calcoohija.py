#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoo
"importamos lo utilizado en el programa calcoo.py"


class CalculadoraHija(calcoo.Calculadora):

    "Esto la clase calculadora"

    def multiplicacion(self):

        "Esta es la función encargada de multiplicar los operandos"

        return self.operando1 * self.operando2

    def division(self):

        "Esta es la función encargada de dividir los operandos"

        if self.operando2 == 0:
            sys.exit("Division by zero is not allowed.")
        else:
            return self.operando1 / self.operando2


if __name__ == "__main__":

    try:

        operando1 = int(sys.argv[1])
        operando2 = int(sys.argv[3])

    except ValueError:
        sys.exit("Error: Non numerical parameters")

    "Se comprueba que los valores del operando1 y operando2 son enteros"

    calcula = CalculadoraHija()
    calcula.init(operando1, operando2)
    if sys.argv[2] == "suma":
        result = calcula.suma()
    elif sys.argv[2] == "resta":
        result = calcula.resta()
    elif sys.argv[2] == "multiplica":
        result = calcula.multiplicacion()
    elif sys.argv[2] == "divide":
        result = calcula.division()
    else:
        sys.exit('Sólo puede ser sumar, restar, multiplicar o dividir')

    "se ejecuta la función suma y resta y comprueba que el operando es valido"

    print(result)
    "imprime el resultado"
