import sqlite3

def agregar_columna_si_no_existe(cursor, tabla, columna, tipo):
    # Verifica si la columna ya existe
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [info[1] for info in cursor.fetchall()]
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
        print(f"✔️ Columna '{columna}' agregada a la tabla '{tabla}'.")
    else:
        print(f"ℹ️ La columna '{columna}' ya existe en '{tabla}'.")

# Conexión
conn = sqlite3.connect("sistema.db")
cursor = conn.cursor()

# Verificaciones para la tabla 'visitas'
print("▶️ Revisando tabla 'visitas'...")
agregar_columna_si_no_existe(cursor, "visitas", "motivo", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "marca", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "modelo", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "color", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "patente", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "fecha_ingreso", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "hora_ingreso", "TEXT")
agregar_columna_si_no_existe(cursor, "visitas", "hora_salida", "TEXT")

# Guardar cambios
conn.commit()
conn.close()
print("✅ Migración completada.")
