# Sistema médico VitalSoft

Un sistema médico simple creado con Flask, MySQL, HTML, Tailwind CSS y JavaScript.

## Características

- Registro de pacientes
- Programación de citas
- Visualización de registros de citas de pacientes

## Instrucciones de configuración

1. Instalar dependencias de Python:
```
pip install flask flask-mysqldb
```

2. Configurar la base de datos MySQL:
```sql
CREATE DATABASE vitalsoft;

USE vitalsoft;

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
```

3. Actualice las credenciales de MySQL en `vitalsoft/app.py` si es necesario.

4. Ejecute la aplicación Flask:
```
python vitalsoft/app.py
```

5. Accede a la aplicación en http://localhost:5000

## Notas

Este es un sistema de demostración simple para la gestión médica.

Tailwind CSS se incluye a través de CDN para estilo.
