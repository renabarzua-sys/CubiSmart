"""CubiSmart: servicios.proyectos."""
from contextlib import closing
from copy import deepcopy
from partidas.calculos_albanileria import calcular_muro
from pathlib import Path
from servicios.base_datos import db_conectar
from servicios.base_datos import db_guardar
from servicios.base_datos import db_leer
from servicios.base_datos import extras_guardar
from servicios.base_datos import extras_leer
from servicios.estado import BASE
from servicios.estado import S
import json
import sqlite3
import streamlit as st

def ficha_proyecto():
    st.header('📋 Antecedentes del proyecto')
    e=extras_leer(S.proyecto_id); f=e.get('ficha',{})
    with st.form('ficha_'+str(S.proyecto_id)):
        valores={k:st.text_input(t,value=f.get(k,''),max_chars=250) for k,t in [('mandante','Mandante'),('responsable','Profesional responsable'),('direccion','Dirección'),('comuna','Comuna'),('empresa','Empresa constructora'),('codigo','Código del proyecto'),('plano','Plano / referencia'),('fecha','Fecha de elaboración')]}
        if st.form_submit_button('Guardar antecedentes',use_container_width=True):
            e['ficha']=valores; extras_guardar(S.proyecto_id,e); st.success('Antecedentes guardados.')


def administrar_proyecto():
    from io import BytesIO
    from tempfile import TemporaryDirectory
    st.header('Administración avanzada')
    pid=S.proyecto_id; nombre,muros=db_leer(pid); e=extras_leer(pid)
    st.caption('Los cambios afectan únicamente al proyecto activo.')
    with st.form('renombrar_'+str(pid)):
        nuevo=st.text_input('Nuevo nombre',value=nombre).strip()
        if st.form_submit_button('Renombrar proyecto'):
            try:
                if not nuevo: raise ValueError('Ingresa un nombre.')
                with closing(db_conectar()) as con, con: con.execute('UPDATE proyectos SET nombre=?, actualizado=CURRENT_TIMESTAMP WHERE id=?',(nuevo,pid))
                S.proyecto_nombre=nuevo; st.rerun()
            except (ValueError,sqlite3.Error) as ex: st.error(str(ex))
    with st.form('duplicar_'+str(pid)):
        copia=st.text_input('Nombre de la copia',value=nombre+' (copia)').strip()
        if st.form_submit_button('Duplicar proyecto'):
            try:
                if not copia: raise ValueError('Ingresa un nombre.')
                with closing(db_conectar()) as con, con:
                    nid=con.execute('INSERT INTO proyectos(nombre,muros) VALUES (?,?)',(copia,json.dumps(muros,ensure_ascii=False))).lastrowid
                    con.execute('INSERT INTO proyecto_extra VALUES (?,?)',(nid,json.dumps(e,ensure_ascii=False)))
                st.success('Copia creada. Ábrela desde Mis proyectos.')
            except (ValueError,sqlite3.Error) as ex: st.error(str(ex))
    if muros:
        with st.form('duplicar_muro_'+str(pid)):
            origen=st.selectbox('Muro original',list(muros)); destino=st.text_input('Nombre del muro duplicado').strip()
            if st.form_submit_button('Duplicar muro'):
                if not destino or destino in muros: st.error('Ingresa un nombre nuevo y único.')
                else:
                    muros[destino]=deepcopy(muros[origen]); db_guardar(pid,muros); S.muros_guardados=muros; st.rerun()
    st.download_button('Exportar proyecto JSON',json.dumps({'version':1,'nombre':nombre,'muros':muros,'extra':e},ensure_ascii=False,indent=2).encode(),'proyecto_cubismart.json','application/json')
    with TemporaryDirectory() as d:
        ruta=Path(d)/'respaldo.db'
        with closing(db_conectar()) as src, closing(sqlite3.connect(str(ruta))) as dst: src.backup(dst)
        respaldo=ruta.read_bytes()
    st.download_button('Descargar respaldo de mis proyectos SQLite',respaldo,'cubismart_respaldo.db','application/octet-stream')
    st.caption('Este respaldo contiene solo tus proyectos, no las cuentas ni contraseñas. Para restaurarlo, cierra Streamlit y reemplaza el archivo SQLite correspondiente a tu usuario en datos_usuarios. Conserva una copia del original.')
    with closing(db_conectar()) as con:
        fecha=con.execute('SELECT actualizado FROM proyectos WHERE id=?',(pid,)).fetchone()[0]
    st.caption('Última modificación de muros o nombre (UTC): '+fecha)
    archivo=st.file_uploader('Importar proyecto JSON',type=['json'])
    if archivo and st.button('Importar como proyecto independiente'):
        try:
            if archivo.size>10_000_000: raise ValueError('Archivo demasiado grande.')
            obj=json.loads(archivo.getvalue()); n=obj['nombre'].strip(); m=obj['muros']; extra=obj.get('extra',{})
            if obj.get('version')!=1 or not n or not isinstance(m,dict) or not isinstance(extra,dict): raise ValueError('Formato no válido.')
            # Recalcular desde datos, nunca confiar en totales importados.
            limpio={}
            for k,r in m.items():
                if not isinstance(k,str) or not k.strip(): raise ValueError('Nombre de muro inválido.')
                datos=r['datos']; cantidad=datos['dato_cantidad_vanos']
                if type(cantidad)!=int or not 0<=cantidad<=30: raise ValueError('Cantidad de vanos inválida.')
                datos={k:datos[k] for k in BASE if not k.startswith(('dato_ancho_vano_', 'dato_alto_vano_')) or int(k.rsplit('_',1)[1])<cantidad}
                rr=calcular_muro(datos); rr['datos']=datos; limpio[k]=rr
            # Importar solo ficha textual; precios/dosificación se configuran de nuevo para evitar datos inválidos.
            ficha=extra.get('ficha',{}); extra={'ficha':{k:v[:250] for k,v in ficha.items() if isinstance(k,str) and isinstance(v,str)}} if isinstance(ficha,dict) else {}
            with closing(db_conectar()) as con, con:
                nid=con.execute('INSERT INTO proyectos(nombre,muros) VALUES (?,?)',(n,json.dumps(limpio,ensure_ascii=False,allow_nan=False))).lastrowid
                con.execute('INSERT INTO proyecto_extra VALUES (?,?)',(nid,json.dumps(extra,ensure_ascii=False)))
            st.success('Proyecto importado. Abre desde Mis proyectos. Configura nuevamente precios y dosificación.')
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError,sqlite3.Error) as ex: st.error('No se pudo importar: '+str(ex))


