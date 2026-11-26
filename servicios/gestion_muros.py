"""CubiSmart: servicios.gestion_muros."""
from copy import deepcopy
from partidas.calculos_albanileria import calcular_muro
from partidas.calculos_albanileria import resultados_vacios
from servicios.base_datos import db_crear
from servicios.base_datos import db_eliminar
from servicios.base_datos import db_guardar
from servicios.base_datos import db_leer
from servicios.estado import BASE
from servicios.estado import PRUEBA
from servicios.estado import S
import sqlite3

def abrir_proyecto(pid):
    nombre, muros = db_leer(pid)
    S.proyecto_id = pid
    S.proyecto_nombre = nombre
    S.muros_guardados = muros
    for clave in list(S.keys()):
        if clave.startswith(('dos_','exp_')):
            del S[clave]
    nuevo_muro()
    if muros:
        S['seleccionar_muro_guardado'] = next(iter(muros))
        cargar_muro(False)
    aviso('success', f'Proyecto abierto: {nombre}.')


def crear_proyecto():
    nombre = S.get('nuevo_nombre_proyecto','').strip()
    if not nombre:
        aviso('error','Ingresa un nombre para el proyecto.'); return
    try:
        pid = db_crear(nombre)
        abrir_proyecto(pid)
        S['selector_proyecto'] = pid
        S['nuevo_nombre_proyecto'] = ''
    except sqlite3.IntegrityError:
        aviso('error','Ya existe un proyecto con ese nombre.')
    except (sqlite3.Error, ValueError) as e:
        aviso('error',f'No se pudo crear el proyecto: {e}')


def cambiar_proyecto():
    try:
        abrir_proyecto(S['selector_proyecto'])
    except (sqlite3.Error, ValueError) as e:
        S['selector_proyecto'] = S.proyecto_id
        aviso('error',f'No se pudo abrir el proyecto: {e}')


def datos_actuales():
    return {k: (BASE[k] if S[k] is None else S[k]) for k in BASE if not k.startswith(('dato_ancho_vano_', 'dato_alto_vano_')) or int(k.rsplit('_',1)[1]) < (S['dato_cantidad_vanos'] or 0)}


def aviso(tipo, mensaje):
    S['aviso'] = (tipo,mensaje)


def nuevo_muro():
    S.update(BASE)
    S.resultados = resultados_vacios()
    S.muro_en_edicion = None
    S['seleccionar_muro_guardado'] = None
    n=1
    while f'Muro {n:02d}' in S.muros_guardados:
        n+=1
    S.dato_nombre_muro=f'Muro {n:02d}'
    S.vista_actual='🧮 Cubicación'
    aviso('success','Formulario listo para un nuevo muro.')


def cargar_datos_prueba():
    S['seleccionar_muro_guardado']=None
    S.update(PRUEBA)
    S.resultados=resultados_vacios()
    S.vista_actual='🧮 Cubicación'
    aviso('success','Datos de prueba cargados.')


def calcular(guardar=False):
    try:
        datos=datos_actuales()
        r=calcular_muro(datos)
        r['datos']=deepcopy(datos)
        S.resultados=r
        if guardar:
            guardar_muro()
        else:
            aviso('success','Cubicación realizada.')
        S.vista_actual='🧮 Cubicación'
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        S.resultados=resultados_vacios()
        aviso('error',str(e))
        S.vista_actual='🧮 Cubicación'


def guardar_muro():
    nombre=S.dato_nombre_muro.strip()
    r=S.resultados
    if not nombre:
        aviso('error','Ingresa un nombre para el muro.'); return
    if not r.get('memoria') or r.get('datos') != datos_actuales():
        aviso('error','Calcula nuevamente antes de guardar.'); return
    anterior=S.muro_en_edicion
    if nombre in S.muros_guardados and nombre != anterior:
        aviso('error','Ya existe un muro con ese nombre.'); return
    nuevos=deepcopy(S.muros_guardados)
    if anterior and anterior != nombre:
        nuevos.pop(anterior,None)
    nuevos[nombre]=deepcopy(r)
    try:
        db_guardar(S.proyecto_id,nuevos)
    except (sqlite3.Error, ValueError) as e:
        aviso('error',f'No se pudo guardar en disco: {e}'); return
    S.muros_guardados=nuevos
    S.muro_en_edicion=nombre
    S['seleccionar_muro_guardado']=nombre
    aviso('success',f'Muro {nombre} guardado.')


def cargar_muro(cambiar_vista=True):
    nombre=S.get('seleccionar_muro_guardado')
    if nombre not in S.muros_guardados: return
    r=deepcopy(S.muros_guardados[nombre])
    S.update(BASE); S.update(r['datos'])
    S.resultados=r; S.dato_nombre_muro=nombre; S.muro_en_edicion=nombre
    if cambiar_vista:
        S.vista_actual='🧮 Cubicación'
    aviso('success',f'Muro {nombre} cargado.')


def eliminar_muro():
    nombre=S.get('seleccionar_muro_guardado')
    if nombre not in S.muros_guardados: return
    nuevos=deepcopy(S.muros_guardados)
    del nuevos[nombre]
    try:
        db_guardar(S.proyecto_id,nuevos)
    except (sqlite3.Error, ValueError) as e:
        aviso('error',f'No se pudo guardar la eliminación: {e}'); return
    S.muros_guardados=nuevos
    if S.muro_en_edicion==nombre:
        nuevo_muro()
    S['seleccionar_muro_guardado']=None
    aviso('success',f'Muro {nombre} eliminado.')


def limpiar_resultados():
    S['seleccionar_muro_guardado']=None
    S.resultados=resultados_vacios()
    aviso('success','Resultados limpiados.')


def abrir_desde_inicio():
    pid = S.get('inicio_selector_proyecto')
    if pid is None:
        aviso('error', 'Selecciona un proyecto para continuar.')
        return
    try:
        abrir_proyecto(pid)
        S['selector_proyecto'] = pid
        S.partida_seleccionada = None
    except (sqlite3.Error, ValueError) as e:
        aviso('error', f'No se pudo abrir el proyecto: {e}')


def crear_desde_inicio():
    nombre = S.get('inicio_nombre_proyecto', '').strip()
    if not nombre:
        aviso('error', 'Ingresa un nombre para el proyecto.')
        return
    try:
        pid = db_crear(nombre)
        abrir_proyecto(pid)
        S['selector_proyecto'] = pid
        S['inicio_nombre_proyecto'] = ''
        S.partida_seleccionada = None
    except sqlite3.IntegrityError:
        aviso('error', 'Ya existe un proyecto con ese nombre.')
    except (sqlite3.Error, ValueError) as e:
        aviso('error', f'No se pudo crear el proyecto: {e}')


def volver_proyectos():
    S.proyecto_id = None
    S.proyecto_nombre = ''
    S.muros_guardados = {}
    nuevo_muro()
    S.partida_seleccionada = None
    S.pop('aviso', None)
    S.pop('selector_proyecto', None)
    S.pop('inicio_selector_proyecto', None)
    S.pop('confirmacion_proyecto', None)
    S.pop('confirmar_borrado_proyecto', None)


def eliminar_proyecto_inicio():
    pid = S.get('inicio_selector_proyecto')
    if pid is None or S.get('confirmacion_proyecto') != pid or not S.get('confirmar_borrado_proyecto', False):
        aviso('error', 'Selecciona y confirma el proyecto que deseas eliminar.')
        return
    try:
        nombre, _ = db_leer(pid)
        db_eliminar(pid)
        if S.proyecto_id == pid:
            volver_proyectos()
        S.pop('inicio_selector_proyecto', None)
        S.pop('confirmacion_proyecto', None)
        S.pop('confirmar_borrado_proyecto', None)
        aviso('success', f'Proyecto eliminado: {nombre}.')
    except (sqlite3.Error, ValueError) as e:
        aviso('error', f'No se pudo eliminar el proyecto: {e}')


def cambiar_seleccion_inicio():
    S.pop('confirmacion_proyecto', None)
    S.pop('confirmar_borrado_proyecto', None)


