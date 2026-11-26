
import streamlit as st
import math
import sqlite3
import json
from pathlib import Path
from contextlib import closing
from copy import deepcopy
import pandas as pd

# ==========================================
# 1. CONFIGURACION GENERAL
# ==========================================

st.set_page_config(
    page_title="CubiSmart | Cubicación de materiales",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)


from partidas.catalogo import CATEGORIAS
from servicios.estado import S, inicializar_estado
from partidas.calculos_albanileria import resultados_vacios, calcular_muro
from servicios.base_datos import db_conectar, db_iniciar, db_listar, db_crear, db_leer, db_guardar, db_eliminar, extras_leer, extras_guardar
from servicios.gestion_muros import abrir_proyecto, crear_proyecto, cambiar_proyecto, datos_actuales, aviso, nuevo_muro, cargar_datos_prueba, calcular, guardar_muro, cargar_muro, eliminar_muro, limpiar_resultados, abrir_desde_inicio, crear_desde_inicio, volver_proyectos, eliminar_proyecto_inicio, cambiar_seleccion_inicio
from partidas.albanileria import mostrar_memoria, titulo_seccion, mostrar_formulario, mostrar_resultados, mostrar_muros, mostrar_resumen, mostrar_dosificacion, control_tecnico
from servicios.exportaciones import filas_exportacion, pasos_exportacion, exportar_excel, exportar_pdf, mostrar_exportacion, costos_exportar
from servicios.presupuestos import cantidades_presupuesto, mostrar_costos
from servicios.proyectos import ficha_proyecto, administrar_proyecto

from servicios.autenticacion import pantalla_acceso, cerrar_sesion

st.markdown("<style>" + (Path(__file__).resolve().parent / "estilos" / "estilos.css").read_text(encoding="utf-8") + "</style>", unsafe_allow_html=True)

if not S.get("usuario_cubismart"):
    pantalla_acceso()
    st.stop()

inicializar_estado()
with st.container(key="cuenta_activa"):
    cuenta, salir = st.columns([3,1])
    with cuenta:
        st.caption("Sesión activa: " + S.usuario_cubismart["nombre"])
    with salir:
        st.button("Cerrar sesión", on_click=cerrar_sesion, use_container_width=True, key="salir_cuenta")

try:
    db_iniciar()
    proyectos = db_listar()
    if 'proyecto_id' not in S:
        S.proyecto_id = None
except (sqlite3.Error, ValueError, OSError) as e:
    st.error(f'No se pudo abrir la base de datos local: {e}')
    st.stop()

st.markdown("""
<div class="hero">
    <span class="hero-tag">HERRAMIENTA DE CUBICACIÓN</span>
    <h1>🧱 CubiSmart</h1>
    <p>
        Crea o abre un proyecto y cubica sus materiales de forma sencilla. 
    </p>
</div>
""", unsafe_allow_html=True)



# Pantalla inicial: seleccionar un proyecto antes de elegir partida.
if S.proyecto_id is None:
    S.pop('categoria_partidas', None)
    st.markdown('## Mis proyectos')
    st.caption('Abre un proyecto guardado o crea uno nuevo para comenzar.')
    if 'aviso' in S:
        tipo, mensaje = S.pop('aviso')
        getattr(st, tipo)(mensaje)
    with st.container(key='inicio_proyectos'):
        col_abrir, col_crear = st.columns(2)
        with col_abrir:
            with st.container(border=True):
                st.markdown('### Abrir proyecto existente')
                if proyectos:
                    st.selectbox('Proyectos guardados', list(proyectos),
                        format_func=lambda pid: proyectos[pid], index=None,
                        placeholder='Selecciona un proyecto', key='inicio_selector_proyecto', on_change=cambiar_seleccion_inicio)
                    st.button('Abrir proyecto', on_click=abrir_desde_inicio,
                        use_container_width=True, disabled=S.get('inicio_selector_proyecto') is None)
                else:
                    st.info('Todavía no tienes proyectos guardados.')
        with col_crear:
            with st.container(border=True):
                st.markdown('### Crear proyecto nuevo')
                st.text_input('Nombre del proyecto', key='inicio_nombre_proyecto',
                    placeholder='Ejemplo: Vivienda un piso')
                st.button('Crear proyecto', on_click=crear_desde_inicio,
                    use_container_width=True)
    if S.get('inicio_selector_proyecto') in proyectos:
        pid = S['inicio_selector_proyecto']
        with st.expander('🗑️ Eliminar proyecto seleccionado'):
            if S.get('confirmacion_proyecto') != pid:
                S['confirmacion_proyecto'] = pid
                S.pop('confirmar_borrado_proyecto', None)
            st.warning(f'Se eliminará permanentemente el proyecto «{proyectos[pid]}» y todos sus muros y memorias de cálculo. Esta acción no se puede deshacer.')
            st.checkbox('Confirmo que deseo eliminar este proyecto', key='confirmar_borrado_proyecto')
            st.button('🗑️ Eliminar proyecto definitivamente', key='confirmar_eliminar_proyecto',
                on_click=eliminar_proyecto_inicio, use_container_width=True,
                disabled=not S.get('confirmar_borrado_proyecto', False))
    st.caption('Los muros guardados se conservan en la base de datos local.')
    st.stop()


if st.session_state.partida_seleccionada is None:

    st.button('← Volver a mis proyectos', key='volver_proyectos_inicio', on_click=volver_proyectos, type='primary', help='Los muros guardados se conservan; los cambios sin guardar se descartan.')
    st.caption('Proyecto activo: ' + S.proyecto_nombre)
    if 'aviso' in S:
        tipo, mensaje = S.pop('aviso')
        getattr(st, tipo)(mensaje)
    if st.button('AutoPlan · Importar y medir planos', key='abrir_autoplan', type='primary', use_container_width=True):
        S.partida_seleccionada='autoplan'; st.rerun()
    categoria = S.get('categoria_partidas')
    if categoria not in CATEGORIAS:
        st.markdown("## ¿Qué deseas cubicar?")
        st.caption("Selecciona una categoría para consultar sus partidas.")
        with st.container(key='menu_categorias'):
            nombres = list(CATEGORIAS)
            for i in range(0, len(nombres), 2):
                columnas = st.columns(2) if i+1 < len(nombres) else [st.container()]
                for col, nombre in zip(columnas, nombres[i:i+2]):
                    with col:
                        if st.button(f"{nombre} · {len(CATEGORIAS[nombre])} partidas", key=f'categoria_{i}_{nombre}', use_container_width=True):
                            S.categoria_partidas = nombre
                            st.rerun()
    else:
        if st.button('← Volver a categorías', key='volver_categorias', type='primary'):
            S.pop('categoria_partidas', None)
            st.rerun()
        st.markdown('## ' + categoria)
        st.caption('Selecciona una partida para comenzar la cubicación.')
        with st.container(key='lista_partidas'):
            for codigo, nombre, unidad in CATEGORIAS[categoria]:
                disponible = codigo == '1.1' or codigo.startswith(('2.','3.','4.','5.'))
                estado = 'Disponible' if disponible else 'Próximamente'
                if st.button(f'{codigo} · {nombre} · {unidad} · {estado}', key='catalogo_'+codigo, disabled=not disponible, use_container_width=True):
                    S.partida_seleccionada = 'trazado' if codigo == '1.1' else ('albanileria' if codigo == '2.9' else codigo)
                    st.rerun()

    # Ocultar los calculos hasta seleccionar una partida
    st.stop()




if S.partida_seleccionada == 'autoplan':
    from autoplan.interfaz import mostrar
    mostrar()
    st.stop()

from partidas.calculos_terminaciones_instalaciones import CAT as CATALOGO_TI
if S.partida_seleccionada in CATALOGO_TI:
    from partidas.terminaciones_instalaciones import mostrar
    mostrar(S.partida_seleccionada)
    st.stop()

from partidas.calculos_techumbre import CAT as CATALOGO_TECHUMBRE
if S.partida_seleccionada in CATALOGO_TECHUMBRE:
    from partidas.techumbre import mostrar
    mostrar(S.partida_seleccionada)
    st.stop()

from partidas.calculos_obra_gruesa import CAT as CATALOGO_OBRA_GRUESA
if S.partida_seleccionada in CATALOGO_OBRA_GRUESA:
    from partidas.obra_gruesa import mostrar
    mostrar(S.partida_seleccionada)
    st.stop()

if S.partida_seleccionada == 'trazado':
    from partidas.trazado import mostrar_trazado
    mostrar_trazado()
    st.stop()


with st.sidebar:
    st.markdown('## 🧱 CubiSmart')
    if st.button('← Volver a elegir partida',key='volver_partidas',use_container_width=True):
        S.partida_seleccionada=None; st.rerun()
    st.button('📁 Volver a mis proyectos', key='volver_proyectos_lateral', on_click=volver_proyectos, type='primary', use_container_width=True, help='Guarda los cambios antes de volver. Los borradores se descartan.')
    st.markdown('### 📁 Proyectos')
    proyectos = db_listar()
    if 'selector_proyecto' not in S:
        S['selector_proyecto'] = S.proyecto_id
    st.selectbox('Proyecto activo', list(proyectos), format_func=lambda pid: proyectos[pid], key='selector_proyecto', on_change=cambiar_proyecto)
    with st.expander('＋ Crear proyecto'):
        st.text_input('Nombre del proyecto', key='nuevo_nombre_proyecto')
        st.button('Crear y abrir', on_click=crear_proyecto, use_container_width=True)
    st.caption('Los muros guardados se conservan en disco. Guarda los cambios antes de cambiar de proyecto.')
    st.markdown('### Navegación')
    vista=st.radio('Vista',['🧮 Cubicación','📋 Memoria de cálculo','📁 Muros guardados','📊 Resumen general','🪣 Dosificación de mortero','📄 Exportar','💰 Presupuesto','🧮 APU','📋 Ficha del proyecto','⚙️ Administración','✅ Control técnico'],key='vista_actual',label_visibility='collapsed', format_func=lambda opcion: '▸ ' + opcion.split(' ', 1)[1])
    st.divider()
    st.markdown('### Gestión de muros')
    st.text_input('Nombre del muro',key='dato_nombre_muro')
    if S.muro_en_edicion: st.caption('Editando: '+S.muro_en_edicion)
    st.button('➕ Nuevo muro',key='nuevo_muro',on_click=nuevo_muro,use_container_width=True)
    if S.muros_guardados:
        st.selectbox('Muros guardados',list(S.muros_guardados),index=None,placeholder='Selecciona un muro',key='seleccionar_muro_guardado',on_change=cargar_muro,args=(False,))
        st.button('✏️ Cargar muro',key='editar_muro',on_click=cargar_muro,use_container_width=True)
        st.button('🗑️ Eliminar muro',key='eliminar_muro',on_click=eliminar_muro,use_container_width=True)
    else: st.caption('No hay muros guardados.')
    st.divider()
    st.markdown('### Operaciones')
    st.button('🧪 Cargar datos de prueba',on_click=cargar_datos_prueba,use_container_width=True)
    st.button('🔄 Restablecer formulario',on_click=nuevo_muro,use_container_width=True)
    st.button('🧮 Calcular cubicación',on_click=calcular,use_container_width=True)
    st.button('💾 Guardar muro',on_click=guardar_muro,use_container_width=True)
    st.button('🧮 Calcular y guardar muro',on_click=calcular,args=(True,),type='primary',use_container_width=True)
    st.button('Limpiar resultados',on_click=limpiar_resultados,use_container_width=True)
    if 'aviso' in S:
        tipo,mensaje=S.pop('aviso'); getattr(st,tipo)(mensaje)
    st.caption('Guardado local automático al guardar o eliminar un muro. Los borradores y ajustes de dosificación no se guardan.')

if vista=='🧮 Cubicación':
    st.markdown('### 🧱 Cubicación de albañilería')
    st.caption('Proyecto activo: '+S.proyecto_nombre)
    st.caption('Trabajando en: '+S.dato_nombre_muro)
    mostrar_formulario()
    if S.resultados.get('memoria') and S.resultados.get('datos')!=datos_actuales():
        st.warning('Has cambiado datos. Los resultados corresponden a la última cubicación; vuelve a calcular.')
    mostrar_resultados()
elif vista=='📋 Memoria de cálculo':
    if S.resultados.get('datos') and S.resultados['datos']!=datos_actuales(): st.warning('Memoria de la última cubicación, no de los datos modificados.')
    mostrar_memoria()
elif vista=='📁 Muros guardados': mostrar_muros()
elif vista=='📊 Resumen general': mostrar_resumen()
elif vista=='📄 Exportar': mostrar_exportacion()
elif vista=='💰 Presupuesto':
    with st.container(key='vista_costos'):
        mostrar_costos()
elif vista=='🧮 APU':
    with st.container(key='vista_costos'):
        mostrar_costos(True)
elif vista=='📋 Ficha del proyecto':
    with st.container(key='vista_ficha'):
        ficha_proyecto()
elif vista=='⚙️ Administración':
    with st.container(key='vista_admin'):
        administrar_proyecto()
elif vista=='✅ Control técnico': control_tecnico()
else:
    if S.resultados.get('datos') and S.resultados['datos']!=datos_actuales(): st.warning('Dosificación basada en la última cubicación; vuelve a calcular si cambiaste datos.')
    mostrar_dosificacion()
st.markdown('<div class="footer">CubiSmart · Cubicación de albañilería</div>',unsafe_allow_html=True)
