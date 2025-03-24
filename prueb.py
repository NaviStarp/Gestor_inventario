import csv

with open('addresses.csv', 'r') as file:
    reader = csv.reader(file)
    columns = next(reader)  # Lee la primera fila como nombres de columnas
    for row in reader:
        for i, field in enumerate(row):
            print(f'{columns[i]}: {field}')

# Importar productos a la base de datos de flask

with open("inventario.csv", "r") as file:
    reader = csv.reader(file)
    columns = next(reader)
    for row in reader:
        print(row)
        # Insertar en la base de datos
        # cursor.execute("INSERT INTO productos (nombre, precio) VALUES (?, ?)", row)
        # connection.commit()