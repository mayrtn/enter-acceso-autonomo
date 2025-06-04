import sqlite3

conn = sqlite3.connect("sistema.db")
cursor = conn.cursor()

# Agregar la columna si no existe
try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN telefono TEXT")
    print("Columna 'telefono' añadida correctamente.")
except sqlite3.OperationalError:
    print("La columna 'telefono' ya existe o falló la modificación.")

conn.commit()
conn.close()
