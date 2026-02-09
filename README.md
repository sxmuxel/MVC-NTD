# MVC-NTD

## Descripción del proyecto

MVC-NTD es una aplicación web desarrollada en Python con **Flask** que implementa el patrón
**Modelo–Vista–Controlador (MVC)** para gestionar información obtenida a partir de
búsquedas de artículos científicos en bases de datos académicas como **Scopus**.

El sistema permite registrar búsquedas, visualizar artículos científicos y gestionar
un CRUD de categorías relacionadas con aplicaciones de **Inteligencia Artificial en la Educación**.

# Procedimiento para ejecutar el código de conexión

## Requisitos y dependencias

- Python 3.9+
- Flask 2.x+
- Flask-SQLAlchemy 3.x+
- SQLite

## Instrucciones de ejecución (Windows)

### Paso 1: Clonar repositorio

En la terminal:
```bash
git clone https://github.com/sxmuxel/MVC-NTD.git
cd MVC-NTD
```

### Paso 2: Crear entorno virtual

En la terminal:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### Paso 3: Instalar dependencias requeridas

En la terminal:
```bash
pip install -r requirements.txt
```

###Paso 4: Ejecutar app.py

En la terminal:
```bash
python app.py
```
