from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from datetime import date

app = FastAPI()

class Usuario(BaseModel):
    nombre: str
    email: str

def get_db_connection():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn


# Crear la tabla de usuarios si no existe
def crear_tabla():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Llamar a la función para crear la tabla al iniciar
crear_tabla()

# ----------------------

# Implementar un endpoint para la creación de un usuario
@app.post("/usuarios")
def crear_usuario(nombre: str, email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO usuarios (nombre, email, fecha_registro)
        VALUES (?, ?, ?)
    ''', (nombre, email, fecha_registro))
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()
    return {"id": usuario_id, "fecha_registro": fecha_registro}

# Implementar un endpoint para la obtención de todos los usuarios
@app.get("/usuarios")
def obtener_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return [dict(usuario) for usuario in usuarios]

# Implementar un endpoint para la obtención de un usuario por ID
@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
    usuario = cursor.fetchone()
    conn.close()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(usuario)

# Implementar otro endpoint para la obtención de un usuario por ID
@app.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, usuario: Usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE usuarios
        SET nombre = ?, email = ?
        WHERE id = ?
    ''', (usuario.nombre, usuario.email, usuario_id))
    conn.commit()
    conn.close()
    return {"id": usuario_id, **usuario.dict()}

# Implementar otro endpoint para la actualización parcial de un usuario
@app.patch("/usuarios/{usuario_id}")
def actualizar_usuario_parcial(usuario_id: int, usuario: Usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
    existing_usuario = cursor.fetchone()
    if existing_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar solo los campos proporcionados
    nombre = usuario.nombre if usuario.nombre else existing_usuario['nombre']
    email = usuario.email if usuario.email else existing_usuario['email']
    
    cursor.execute('''
        UPDATE usuarios
        SET nombre = ?, email = ?
        WHERE id = ?
    ''', (nombre, email, usuario_id))
    conn.commit()
    conn.close()
    return {"id": usuario_id, "nombre": nombre, "email": email}

# Implementar otro endpoint para la eliminación de un usuario
@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario eliminado correctamente"}

# ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
