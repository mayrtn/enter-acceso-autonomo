PRAGMA foreign_keys = ON;

-- Tabla Barrios
CREATE TABLE barrios (
    id_barrio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);

-- Tabla Lotes
CREATE TABLE lotes (
    id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_lote TEXT NOT NULL,
    id_barrio INTEGER NOT NULL,
    FOREIGN KEY (id_barrio) REFERENCES barrios(id_barrio)
);

-- Tabla Usuarios
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- TODO hashear
    rol_usuario TEXT NOT NULL, -- Esperados: 'propietario', 'admin', 'seguridad'
    id_barrio INTEGER NOT NULL,
    pin_acceso TEXT,             -- PIN de acceso válido
    pin_seguridad TEXT,          -- PIN que alerta silenciosa
    intentos_fallidos INTEGER DEFAULT 0, -- Cantidad de intentos fallido para bloquear el sistema 
    bloqueado BOOLEAN DEFAULT 0, --default False
    FOREIGN KEY (id_barrio) REFERENCES barrios(id_barrio)
);

-- Tabla Vehículos asociados a usuarios (1 usuario puede tener varios vehículos)
CREATE TABLE vehiculos (
    id_vehiculo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    color TEXT NOT NULL,
    patente TEXT NOT NULL UNIQUE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla intermedia: relación usuarios-lotes (muchos a muchos)
CREATE TABLE usuarios_lotes (
    id_usuario INTEGER NOT NULL,
    id_lote INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_lote),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_lote) REFERENCES lotes(id_lote)
);

-- Tabla Invitaciones
CREATE TABLE invitaciones (
    id_invitacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,  -- quien invita (propietario)
    nombre_visitante TEXT,
    dni_visitante TEXT,
    email_visita TEXT, NOT NULL
    hora_visita TEXT, NOT NULL
    fecha_visita TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'noAprobada',
    token TEXT NOT NULL UNIQUE,
    comentario TEXT,
    vehiculo BOOLEAN DEFAULT 1,              -- 0: no, 1: sí
    patente TEXT,                          -- Patente si entra en auto
    imagen_poliza TEXT,                    -- Ruta o nombre del archivo subido (póliza de seguro)
    cantiadad_acompanantes INTEGER,
    acompanantes_mayores TEXT,            -- Lista de DNIs separados por coma
    acompanantes_menores TEXT,            -- Lista de nombres y apellidos separados por coma
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE accesos (
    id_acceso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_invitacion INTEGER, -- Puede ser NULL si no hubo invitación
    id_guardia INTEGER NOT NULL,
    fecha_hora_ingreso TEXT NOT NULL,
    fecha_hora_salida TEXT,
    estado TEXT NOT NULL DEFAULT 'noAprobado', 
    -- Valores esperados: 'noAprobado', 'enCurso', 'finalizado'
    token_qr TEXT NOT NULL DEFAULT 'manual', --inicializa por defecto en 'manual' para los accesos que no tienen qr    
    dni_visitante TEXT NOT NULL,
    dni_acompañantes TEXT, -- Lista de DNIs separados por coma (si hay)
    cantidad_acompañantes INTEGER DEFAULT 0, -- Puede ser 0 o más
    hay_acompañante_menor BOOLEAN DEFAULT 0, -- 0: no, 1: sí
    patente TEXT, -- Opcional
    
    FOREIGN KEY (id_invitacion) REFERENCES invitaciones(id_invitacion),
    FOREIGN KEY (id_guardia) REFERENCES usuarios(id_usuario)
);

-- Tabla para gestionar las llaves virtuales temporales de los residentes
CREATE TABLE llaves_virtuales (
    id_llave INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,      -- El residente que generó la llave
    token TEXT NOT NULL UNIQUE,       -- El token único del QR
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now'))
    fecha_expiracion TEXT NOT NULL,   -- Cuándo deja de ser válida
    estado TEXT NOT NULL DEFAULT 'valida', -- 'valida', 'usada'
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
); 