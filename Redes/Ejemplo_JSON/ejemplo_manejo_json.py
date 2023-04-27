import json

# abrimos el archivo del inventario
with open("inventario.json") as file:
    # usamos json para manejar los datos
    data = json.load(file)
    # calculamos la cantidad total de artículos de oficina en el inventario
    total_articulos_de_oficina = 0
    for articulo in data['oficina']:
        cantidad_articulo = articulo['cantidad_total']
        total_articulos_de_oficina += cantidad_articulo

# imprimimos un mensaje indicando la cantidad total de artículos de oficina
print("Hay un total de " + str(total_articulos_de_oficina) + " de artículos de oficina")