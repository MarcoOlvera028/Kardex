# db/conexion.py
import sqlite3
from pathlib import Path

from utils.rutas import ruta_recurso

DB_PATH = ruta_recurso("kardex.db")


def obtener_conexion():
    """
    Abre una conexión a la base de datos SQLite.
    """
    return sqlite3.connect(str(DB_PATH))


def ejecutar_consulta(sql, params=()):
    """
    Ejecuta INSERT, UPDATE o DELETE.
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()


def obtener_fila(sql, params=()):
    """
    Obtiene una única fila (o None si no existe).
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute(sql, params)
    fila = cur.fetchone()
    conn.close()
    return fila


def obtener_todos(sql, params=()):
    """
    Obtiene varias filas como lista de tuplas.
    """
    conn = obtener_conexion()
    cur = conn.cursor()
    cur.execute(sql, params)
    filas = cur.fetchall()
    conn.close()
    return filas
