import sqlite3
from werkzeug.security import generate_password_hash

# Conectamos a la base de datos
conn = sqlite3.connect("sistema.db")
cur = conn.cursor()

# Lista de usuarios de prueba: (nombre, dni, telefono, email, unidad_funcional, contraseña, pin_acceso, pin_seguridad, rol)
usuarios = [
    ("Admin User", "12345678", "1122334455", "admin@ejemplo.com", "UF1", "admin123", "1111", "9999", "admin"),
    ("Guardia Juan", "23456789", "2233445566", "guardia@ejemplo.com", "UF2", "seguridad123", "2222", "8888", "seguridad"),
    ("Carlos Propietario", "34567890", "3344556677", "carlos@ejemplo.com", "UF3", "prop123", "3333", "7777", "propietario"),
]

for nombre, dni, telefono, email, unidad_funcional, contraseña, pin_acceso, pin_seguridad, rol in usuarios:
    hash_contraseña = generate_password_hash(contraseña)
    cur.execute("""
        INSERT INTO usuarios (
            nombre, dni, telefono, email, unidad_funcional,
            contraseña, pin_acceso, pin_seguridad,
            intentos_fallidos, bloqueado, rol, activo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 1)
    """, (
        nombre, dni, telefono, email, unidad_funcional,
        hash_contraseña, pin_acceso, pin_seguridad,
        rol
    ))

conn.commit()
conn.close()
print("✅ Usuarios de prueba creados correctamente.")
