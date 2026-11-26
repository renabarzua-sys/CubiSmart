"""Recuperación local para el propietario del equipo. No es una pantalla web."""
import getpass
import sqlite3
import secrets
from contextlib import closing
from servicios import autenticacion as a


def restablecer(correo, clave):
    if not a.AUTH_DB.is_file():
        raise ValueError('No se encontró la base de cuentas original. No se ha creado otra.')
    if not 10 <= len(clave) <= 128:
        raise ValueError('La contraseña debe tener entre 10 y 128 caracteres.')
    correo = correo.strip().casefold()
    with closing(sqlite3.connect(str(a.AUTH_DB), timeout=30)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT id FROM usuarios WHERE correo=?', (correo,)).fetchone()
        if row is None:
            raise ValueError('No existe esa cuenta en esta base de datos.')
        sal = secrets.token_bytes(32)
        con.execute('UPDATE usuarios SET sal=?,clave=?,iteraciones=?,intentos=0,bloqueado_hasta=0 WHERE id=?', (sal,a.derivar(clave,sal),a.ITERACIONES,row[0]))
        columnas = {r[1] for r in con.execute('PRAGMA table_info(usuarios)')}
        if 'version' in columnas:
            con.execute('UPDATE usuarios SET version=version+1 WHERE id=?',(row[0],))
        if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='codigos'").fetchone():
            con.execute('DELETE FROM codigos WHERE uid=?',(row[0],))


def main():
    print('Recuperación local de CubiSmart. Solo para el propietario autorizado del equipo.')
    print('Base de cuentas:', a.AUTH_DB)
    if not a.AUTH_DB.is_file():
        print('No se encontró la base de cuentas. Busca la carpeta original o un respaldo.'); return
    correo = input('Correo de tu cuenta: ').strip()
    clave = getpass.getpass('Nueva contraseña (mínimo 10 caracteres): ')
    if clave != getpass.getpass('Repetir contraseña: '):
        print('Las contraseñas no coinciden. No se modificó nada.'); return
    if input('Escribe CAMBIAR para confirmar: ') != 'CAMBIAR': return
    try:
        restablecer(correo, clave)
        print('Contraseña actualizada. Se conservaron el ID de usuario y sus proyectos.')
    except (ValueError, sqlite3.Error, OSError) as e:
        print('No se pudo actualizar:', e)


if __name__ == '__main__': main()
