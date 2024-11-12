CREATE TABLE Perfiles (
    id_perfil SERIAL PRIMARY KEY,
    tipo_perfil VARCHAR(20) NOT NULL CHECK (tipo_perfil IN ('usuario', 'profesional', 'administrador'))
);

CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo_documento VARCHAR(20) NOT NULL,
    numero_documento VARCHAR(20) UNIQUE NOT NULL,
    celular VARCHAR(20) NOT NULL,
    correo VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(100) NOT NULL,
    tipo_perfil VARCHAR(20) NOT NULL DEFAULT 'usuario' CHECK (tipo_perfil IN ('usuario', 'profesional', 'administrador'))
);

INSERT INTO Perfiles (tipo_perfil) VALUES 
    ('usuario'), 
    ('profesional'), 
    ('administrador');

CREATE TABLE Profesionales (
    id_profesional SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    especialidad VARCHAR(50) NOT NULL,
    correo VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(100) NOT NULL
);

INSERT INTO Profesionales (nombre, especialidad, correo, contrasena) VALUES
    ('Ana López', 'Psicología Clínica y de la Salud', 'ana@gmail.com', 'Anital12*'),
    ('Luis Martínez', 'Psicología Educativa', 'luis@gmail.com', 'Luisito00.'),
    ('Elena Sánchez', 'Psicología Cognitiva', 'elena@gmail.com', 'Elen9696.'),
    ('Mario García', 'Neuropsicología', 'mario@gmail.com', 'Mariob15.'),
    ('Sara Rodríguez', 'Psicología Biológica', 'sara@gmail.com', 'Sarara89.');

CREATE TABLE Administradores (
    id_administrador SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    correo VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(100) NOT NULL
);

INSERT INTO Administradores (nombre, correo, contrasena) VALUES
    ('Maria Jose Fonseca', 'mjfonseca19@gmail.com', 'Majo123*');

CREATE TABLE Consultas (
    id_consulta SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_profesional INT,
    fecha_consulta DATE NOT NULL,
    hora_consulta TIME NOT NULL,
    motivo TEXT NOT NULL,
    diagnostico TEXT,
    tratamiento TEXT,
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Tomada')),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES Profesionales(id_profesional) ON DELETE CASCADE
);

CREATE TABLE Emociones (
    id_emocion SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_emocion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    emocion VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

CREATE TABLE profesionales_usuarios (
    id_profesional INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_profesional) REFERENCES Profesionales(id_profesional) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION actualizar_estado_consultas() RETURNS VOID AS $$
BEGIN
    UPDATE Consultas
    SET estado = 'Tomada'
    WHERE estado = 'Pendiente' AND fecha_consulta < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('ActualizarEstadoConsultas', '0 0 * * *', 'SELECT actualizar_estado_consultas();');



