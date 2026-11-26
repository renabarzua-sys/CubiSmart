"""Cuentas locales, sin dependencias externas. Contraseñas PBKDF2-SHA256."""
import hashlib
import hmac
import secrets
import sqlite3
import re
import time
from pathlib import Path
from contextlib import closing

ROOT = Path(__file__).resolve().parent.parent
AUTH_DB = ROOT / 'cubismart_usuarios.db'
LEGACY_DB = ROOT / 'cubismart_proyectos.db'
DATA_DIR = ROOT / 'datos_usuarios'
ITERACIONES = 600_000


def conectar():
    con = sqlite3.connect(str(AUTH_DB), timeout=30)
    con.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT UNIQUE NOT NULL,
        sal BLOB NOT NULL, clave BLOB NOT NULL, iteraciones INTEGER NOT NULL,
        intentos INTEGER NOT NULL DEFAULT 0, bloqueado_hasta REAL NOT NULL DEFAULT 0)''')
    return con


def derivar(clave, sal, iteraciones=ITERACIONES):
    return hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), sal, iteraciones)


def ruta_usuario(uid):
    if not isinstance(uid, str) or not re.fullmatch(r'[a-f0-9]{32}', uid):
        raise ValueError('Sesión inválida.')
    return DATA_DIR / (uid + '.db')


def registrar(nombre, correo, clave):
    nombre, correo = nombre.strip(), correo.strip().casefold()
    if not nombre or len(nombre)>100: raise ValueError('Ingresa un nombre válido.')
    if len(correo)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', correo): raise ValueError('Ingresa un correo válido.')
    if not 10 <= len(clave) <= 128: raise ValueError('La contraseña debe tener entre 10 y 128 caracteres.')
    uid, sal = secrets.token_hex(16), secrets.token_bytes(32)
    digest = derivar(clave, sal)
    with closing(conectar()) as con, con:
        con.execute('BEGIN IMMEDIATE')
        primero = con.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0] == 0
        if con.execute('SELECT 1 FROM usuarios WHERE correo=?',(correo,)).fetchone(): raise ValueError('Ya existe una cuenta con ese correo.')
        DATA_DIR.mkdir(exist_ok=True)
        destino = ruta_usuario(uid)
        try:
            if primero and LEGACY_DB.is_file():
                with closing(sqlite3.connect(str(LEGACY_DB))) as src, closing(sqlite3.connect(str(destino))) as dst:
                    src.backup(dst)
            con.execute('INSERT INTO usuarios(id,nombre,correo,sal,clave,iteraciones) VALUES (?,?,?,?,?,?)',(uid,nombre,correo,sal,digest,ITERACIONES))
            con.commit()
        except Exception:
            destino.unlink(missing_ok=True)
            raise
    return primero and LEGACY_DB.is_file()


class AccesoTemporalmenteBloqueado(Exception):
    pass


def autenticar(correo, clave):
    correo = correo.strip().casefold()
    if len(clave)>128 or len(correo)>254: return None
    with closing(conectar()) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row=con.execute('SELECT id,nombre,sal,clave,iteraciones,intentos,bloqueado_hasta FROM usuarios WHERE correo=?',(correo,)).fetchone()
        if not row:
            derivar(clave, b'\x00'*32)
            return None
        uid,nombre,sal,digest,it,intentos,bloqueo=row
        if bloqueo>time.time():
            raise AccesoTemporalmenteBloqueado(max(1, int(bloqueo-time.time())+1))
        if not hmac.compare_digest(derivar(clave,sal,it),digest):
            intentos += 1
            con.execute('UPDATE usuarios SET intentos=?,bloqueado_hasta=? WHERE id=?',(0 if intentos>=5 else intentos,time.time()+60 if intentos>=5 else 0,uid))
            return None
        con.execute('UPDATE usuarios SET intentos=0,bloqueado_hasta=0 WHERE id=?',(uid,))
        return {'id':uid,'nombre':nombre,'correo':correo}


def cerrar_sesion():
    import streamlit as st
    st.session_state.clear()


def pantalla_acceso():
    import streamlit as st
    st.markdown('''<div class="hero"><span class="hero-tag">ACCESO A CUBISMART</span><h1>CubiSmart</h1><p>Tu espacio de cubicación y presupuestos.</p></div>''',unsafe_allow_html=True)
    with st.container(key='acceso_cubismart'):
        st.header('Bienvenido a CubiSmart')
        if st.session_state.pop('registro_exitoso',False):
            st.session_state['modo_acceso'] = 'Iniciar sesión'
            st.success('Cuenta creada. Ahora puedes iniciar sesión.')
        modo = st.radio('Tipo de acceso', ['Iniciar sesión','Crear cuenta'], horizontal=True, key='modo_acceso', label_visibility='collapsed')
        if modo == 'Iniciar sesión':
            with st.form('login',clear_on_submit=True):
                correo=st.text_input('Correo electrónico',max_chars=254,key='login_correo',autocomplete='username')
                clave=st.text_input('Contraseña',type='password',max_chars=128,key='login_clave',autocomplete='current-password')
                enviar=st.form_submit_button('Iniciar sesión',type='primary',use_container_width=True)
            if enviar:
                try:
                    usuario=autenticar(correo,clave)
                    if usuario:
                        st.session_state.clear()
                        st.session_state['usuario_cubismart']=usuario
                        st.rerun()
                    else: st.error('Correo o contraseña incorrectos. Comprueba los datos de tu cuenta.')
                except AccesoTemporalmenteBloqueado as ex: st.warning(f'Acceso temporalmente bloqueado. Intenta de nuevo en {ex.args[0]} segundos.')
                except (sqlite3.Error,OSError) as ex: st.error(f'No se pudo acceder a las cuentas locales ({type(ex).__name__}). Comprueba que estás ejecutando CubiSmart desde tu carpeta original y que la base de datos es accesible.')
        else:
            st.caption('Si eres el primer usuario, se copiarán los proyectos de la versión anterior a tu cuenta.')
            with st.form('registro',clear_on_submit=True):
                nombre=st.text_input('Nombre completo',max_chars=100,key='registro_nombre',autocomplete='name')
                correo=st.text_input('Correo electrónico',max_chars=254,key='registro_correo',autocomplete='email')
                clave=st.text_input('Contraseña (mínimo 10 caracteres)',type='password',max_chars=128,key='registro_clave',autocomplete='new-password')
                repetir=st.text_input('Confirmar contraseña',type='password',max_chars=128,key='registro_repetir',autocomplete='new-password')
                enviar=st.form_submit_button('Registrarme',type='primary',use_container_width=True)
            if enviar:
                try:
                    if clave!=repetir: raise ValueError('Las contraseñas no coinciden.')
                    registrar(nombre,correo,clave)
                    st.session_state['registro_exitoso']=True
                    st.rerun()
                except ValueError as ex: st.error(str(ex))
                except (sqlite3.Error,OSError): st.error('No se pudo crear la cuenta local.')
    st.caption('Las cuentas se almacenan en este equipo. No se envían correos de confirmación.')
