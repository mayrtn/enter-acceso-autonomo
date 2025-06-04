import sqlite3

def crear_tabla_convivientes():
    conn = sqlite3.connect("sistema.db")  # Cambiá el nombre si usás otra base
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS convivientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        mayor_edad INTEGER NOT NULL,
        dni TEXT,
        email TEXT,
        telefono TEXT,
        relacion TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ La tabla 'convivientes' ha sido creada con éxito.")

if __name__ == "__main__":
    crear_tabla_convivientes()
