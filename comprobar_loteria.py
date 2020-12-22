#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
import time


api_url = 'http://api.elpais.com/ws/LoteriaNavidadPremiados'
# api_url + '?n=33488' --> comprueba el número 33488
# api_url + '?s=1'  --> pide status del sorteo

########################################################
# Métodos auxiliares
########################################################

# Estado del sorteo
def draw_status():
  response = requests.get(f'{api_url}?s=1')
  json_data = json.loads(response.text[response.text.find('{'):])
  if not json_data['error']:
    return json_data["status"]
  else:
    return -1

# Mensaje del estado del sorteo
def draw_status_message():
  status_msg = [
    "El sorteo no ha comenzado aún. Todos los números aparecerán como no premiados.",
    "El sorteo ha empezado. La lista de números premiados se va cargando poco a poco. \nUn número premiado podría llegar a tardar unos minutos en aparecer.",
    "El sorteo ha terminado y la lista de números y premios debería ser la correcta aunque, tomada al oído, no podemos estar seguros de ella.",
    "El sorteo ha terminado y existe una lista oficial en PDF.",
    "El sorteo ha terminado y la lista de números y premios está basada en la oficial. \nDe todas formas, recuerda que la única lista oficial es la que publica la ONLAE y deberías comprobar todos tus números contra ella."
  ]
  result = draw_status()
  if result >= 0:
    return status_msg[result]
  else:
    return "ERROR"

# Comprobar el premio de un número
def check_number(number):
  response = requests.get(f'{api_url}?n={number}')
  json_data = json.loads(response.text[response.text.find('{'):])
  result = 'error' if json_data['error'] else int(json_data['premio'])
  return result

########################################################
# Método principal
########################################################
def main():
    """Recibe una lista de números en un fichero, uno en cada línea, y devuelve el premio"""
    
    if len(sys.argv) != 2:
        print('\nPor favor, introduzca el nombre de fichero con la lista de números.')
        print(sys.argv[0] + ' <fichero_con_numeros>\n')
        return 2

    input_file = sys.argv[1]

    try:
        with open(input_file) as in_f:
            lines = in_f.readlines()
    except FileNotFoundError:
        print(f'\nNo se encuentra el fichero {input_file}\n')
        return 1
        
    try:
        lines = [int(x.strip()) for x in lines]
    except ValueError:
        print('\nAsegúrese de que en cada línea sólo haya un número y de que tenga el formato correcto.\n')
        return 1

    # Dar la fecha del sorteo para estos resultados
    response = requests.get(f'{api_url}?t=1')
    json_data = json.loads(response.text[response.text.find('{'):])
    if not json_data['error']:
        ts = time.gmtime(json_data['timestamp'])
        tm_st = time.strftime("%d/%m/%Y", ts)
        print(f'\nLos resultados para este sorteo son de fecha: {tm_st}\n')

    # Dar la situación del sorteo
    print(f'{draw_status_message()}\n')

    # Hacemos un primer recorrido inicial por los números:
    for n in lines:
      print(f'El décimo del número {n:05} tiene un premio de: {check_number(n):,}')
    print()

    # Mientras el estado del sorteo sea menos a 2 quiere decir que todavía pueden salir nuevos números,
    # por lo que continuamos comprobando los resultados cada X tiempo
    # Almacenamos en un array los números premiados (estos no será necesario consultarlos de nuevo)
    winning_numbers = []
    if draw_status() == 1:
      print('El sorteo se está realizando. Iremos comprobando números e indicado los premiados a continuación:')

    while draw_status() == 1 and not len(winning_numbers) == len(lines):
      # Dar los premios para cada número
      for n in lines:
        if not n in winning_numbers:
          prize = check_number(n)
          if prize > 0:
            winning_numbers.append(n)
            print(f'El décimo del número {n:05} tiene un premio de: {prize:,}')
      time.sleep(120)

    print()
    if len(winning_numbers) == len(lines):
      print('¡Enhorabuena! El sorteo ha terminado y todos tus números han sido premiados. Aún así recuerda comprobarlos en la fuente oficial')
    else:
      print(f'El sorteo ha terminado y has conseguido {len(winning_numbers)} premios de {len(lines)} números')

    return 0


if __name__ == '__main__':
    sys.exit(main())
