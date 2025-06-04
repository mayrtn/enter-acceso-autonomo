import sqlite3

def agregar_columnas():
    conn = sqlite3.connect("sistema.db")  # ← Cambiá el nombre si usás otro
    cursor = conn.cursor()

    columnas = {
        "direccion": "TEXT",
        "telefono": "TEXT",
        "patente": "TEXT",
        "pin_acceso": "TEXT",
        "pin_seguridad": "TEXT"
    }

    for columna, tipo in columnas.items():
        try:
            cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {columna} {tipo}")
            print(f"✅ Columna '{columna}' agregada.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"ℹ️ La columna '{columna}' ya existe, se omite.")
            else:
                print(f"❌ Error al agregar la columna '{columna}': {e}")

    conn.commit()
    conn.close()
    print("🎉 Migración finalizada con éxito.")

if __name__ == "__main__":
    agregar_columnas()
