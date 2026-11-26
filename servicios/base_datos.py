"""CubiSmart: servicios.base_datos."""
from contextlib import closing
from pathlib import Path
import json
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "cubismart_proyectos.db"

def db_conectar():
    import streamlit as st
    from servicios.autenticacion import ruta_usuario
    usuario=st.session_state.get("usuario_cubismart")
    if not usuario: raise ValueError("Debes iniciar sesión.")
    ruta=ruta_usuario(usuario["id"])
    ruta.parent.mkdir(exist_ok=True)
    con=sqlite3.connect(str(ruta), timeout=10)
    con.execute("PRAGMA foreign_keys=ON")
    return con


def db_iniciar():
    with closing(db_conectar()) as con, con:
        con.execute("""CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE,
            muros TEXT NOT NULL DEFAULT '{}',
            actualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")

    with closing(db_conectar()) as con, con:
        con.execute("CREATE TABLE IF NOT EXISTS proyecto_extra (pid INTEGER PRIMARY KEY REFERENCES proyectos(id) ON DELETE CASCADE, contenido TEXT NOT NULL)")


def db_listar():
    with closing(db_conectar()) as con:
        return dict(con.execute("SELECT id, nombre FROM proyectos ORDER BY nombre COLLATE NOCASE"))


def db_crear(nombre):
    with closing(db_conectar()) as con, con:
        return con.execute("INSERT INTO proyectos(nombre) VALUES (?)", (nombre,)).lastrowid


def db_leer(pid):
    with closing(db_conectar()) as con:
        fila = con.execute("SELECT nombre, muros FROM proyectos WHERE id=?", (pid,)).fetchone()
    if fila is None:
        raise ValueError("El proyecto no existe.")
    return fila[0], json.loads(fila[1])


def db_guardar(pid, muros):
    contenido = json.dumps(muros, ensure_ascii=False, allow_nan=False)
    with closing(db_conectar()) as con, con:
        cursor = con.execute("UPDATE proyectos SET muros=?, actualizado=CURRENT_TIMESTAMP WHERE id=?", (contenido, pid))
        if cursor.rowcount != 1:
            raise ValueError("El proyecto no existe.")


def db_eliminar(pid):
    with closing(db_conectar()) as con, con:
        cursor = con.execute("DELETE FROM proyectos WHERE id=?", (pid,))
        if cursor.rowcount != 1:
            raise ValueError("El proyecto no existe.")


def extras_leer(pid):
    with closing(db_conectar()) as con:
        row=con.execute('SELECT contenido FROM proyecto_extra WHERE pid=?',(pid,)).fetchone()
    return json.loads(row[0]) if row else {}


def extras_guardar(pid, contenido):
    with closing(db_conectar()) as con, con:
        con.execute('INSERT INTO proyecto_extra(pid,contenido) VALUES (?,?) ON CONFLICT(pid) DO UPDATE SET contenido=excluded.contenido',(pid,json.dumps(contenido,ensure_ascii=False,allow_nan=False)))


