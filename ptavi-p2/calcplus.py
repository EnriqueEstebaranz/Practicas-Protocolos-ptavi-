#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoohija
"importamos lo utilizado en el programa calcoohija.py"


if __name__ == "__main__":

    calculo = calcoohija.CalculadoraHija()

    f = open(sys.argv[1], mode='r', encoding='utf-8')
    for line in f.readlines():
        try:
            lista_calc = line.split(",")
            lista_int = list(map(int, lista_calc[1:]))
            operando1 = lista_int[0]

            for operando2 in lista_int[1:]:
                calculo.init(operando1, operando2)
                if lista_calc[0] == "suma":
                    operando1 = calculo.suma()
                    result = operando1
                elif lista_calc[0] == "resta":
                    operando1 = calculo.resta()
                    result = operando1
                elif lista_calc[0] == "multiplica":
                    operando1 = calculo.multiplicacion()
                    result = operando1
                elif lista_calc[0] == "divide":
                    operando1 = calculo.division()
                    result = operando1
                else:
                    result = 'Sólo puede sumar, restar, multiplicar o dividir'
        except ValueError:
            result = "Error: Non numerical parameters"

        print(result)
    f.close()
