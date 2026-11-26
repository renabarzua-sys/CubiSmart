"""Partida 1.1. Registros independientes en los antecedentes del proyecto."""
import streamlit as st
from servicios.campos import numero as campo_numero
import pandas as pd
from io import BytesIO
from xml.sax.saxutils import escape
from servicios.estado import S
from servicios.base_datos import extras_leer, extras_guardar
from servicios.gestion_muros import volver_proyectos
from partidas.albanileria import titulo_seccion
from partidas.calculos_trazado import calcular_sector, calcular_recursos

def leer():
    return extras_leer(S.proyecto_id).get('trazado_1_1', {'sectores':{},'recursos':{}})

def guardar(datos):
    e=extras_leer(S.proyecto_id); e['trazado_1_1']=datos; extras_guardar(S.proyecto_id,e)

def tablas(datos):
    sectores=[calcular_sector(r['nombre'],r['cantidad'],r['largo'],r['ancho'],r['descuento']) for r in datos['sectores'].values()]
    area=sum(r['neto'] for r in sectores)
    recursos=calcular_recursos(area,datos['recursos'].values())
    a=pd.DataFrame(sectores,columns=['nombre','cantidad','largo','ancho','descuento','bruto','neto']).rename(columns={'nombre':'Sector','cantidad':'Cantidad','largo':'Largo (m)','ancho':'Ancho (m)','descuento':'Descuento (m²)','bruto':'Bruto (m²)','neto':'Neto (m²)'})
    b=pd.DataFrame(recursos,columns=['tipo','nombre','unidad','consumo','perdida','precio','cantidad','costo_unitario','total']).rename(columns={'tipo':'Tipo','nombre':'Recurso','unidad':'Unidad','consumo':'Consumo por m²','perdida':'Pérdida (%)','precio':'Precio ($)','cantidad':'Cantidad total','costo_unitario':'Costo por m² ($)','total':'Total ($)'})
    return area,a,b

def exportar(datos, proyecto):
    area,a,b=tablas(datos); total=float(b['Total ($)'].sum()); pu=float(b['Costo por m² ($)'].sum())
    resumen=pd.DataFrame([{'Proyecto':proyecto,'Ítem':'1.1','Partida':'Trazado y niveles','Unidad':'m²','Cantidad':area,'PU ($)':pu,'Total ($)':total}])
    x=BytesIO()
    with pd.ExcelWriter(x,engine='xlsxwriter') as w:
        for nombre,df in [('Resumen',resumen),('Memoria',a),('APU',b)]:
            df.to_excel(w,sheet_name=nombre,index=False)
            w.sheets[nombre].set_column(0,len(df.columns)-1,22)
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    out=BytesIO(); styles=getSampleStyleSheet(); story=[Paragraph('CubiSmart | 1.1 Trazado y niveles',styles['Title']),Paragraph(escape(proyecto),styles['Normal']),Spacer(1,10),Paragraph(f'Superficie neta: {area:.3f} m² | Precio unitario: $ {pu:,.2f} | Total directo: $ {total:,.2f}',styles['Normal']),Spacer(1,12)]
    for title,df in [('Memoria de cálculo',a),('Recursos y APU',b)]:
        story.append(Paragraph(title,styles['Heading2']))
        rows=[[Paragraph(escape(str(c)),styles['Normal']) for c in df.columns]]
        for row in df.itertuples(index=False,name=None):
            rows.append([Paragraph(escape(f'{v:,.3f}' if isinstance(v,float) else str(v)),styles['Normal']) for v in row])
        t=Table(rows,repeatRows=1,colWidths=[735/len(df.columns)]*len(df.columns)); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDF0E8')),('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.extend([t,Spacer(1,12)])
    SimpleDocTemplate(out,pagesize=landscape(A4),leftMargin=45,rightMargin=45).build(story)
    return x.getvalue(),out.getvalue()

def mostrar_trazado():
    with st.sidebar:
        st.markdown('## CubiSmart')
        st.caption('1.1 · Trazado y niveles')
        if st.button('← Volver a elegir partida',key='volver_trazado',use_container_width=True):
            S.partida_seleccionada=None; st.rerun()
        st.button('Volver a mis proyectos',on_click=volver_proyectos,key='trazado_proyectos',use_container_width=True)
        st.divider()
        st.markdown('### Navegación')
        vista=st.radio('Navegación',['Cubicación','Memoria de cálculo','Sectores guardados','Presupuesto y APU','Exportar','Control técnico'],key='trazado_vista', label_visibility='collapsed', format_func=lambda opcion: '▸ ' + opcion)
    with st.container(key='partida_panel'):
        mostrar_contenido(vista)
    st.markdown('<div class="footer">CubiSmart · Trazado y niveles</div>',unsafe_allow_html=True)

def mostrar_contenido(vista):
    st.markdown('### 1.1 · Trazado y niveles')
    st.caption('Proyecto activo: '+S.proyecto_nombre+' · Unidad de partida: m²')
    datos=leer(); area,a,b=tablas(datos)
    st.metric('Superficie neta acumulada',f'{area:,.3f} m²')
    if vista=='Cubicación':
        titulo_seccion('01', 'Dimensiones del sector')
        st.caption('Una fila por sector rectangular. No sumes superficies superpuestas. Para formas irregulares, divide en rectángulos sin solapes.')
        ids=list(datos['sectores']); sel=st.selectbox('Sector a editar o duplicar',['Nuevo']+ids,format_func=lambda k:'Nuevo sector' if k=='Nuevo' else datos['sectores'][k]['nombre'],key=f'trazado_sel_{S.proyecto_id}')
        r=datos['sectores'].get(sel,{})
        with st.form(f'trazado_form_{S.proyecto_id}_{sel}'):
            nombre=st.text_input('Nombre del sector / eje',value=r.get('nombre',''),max_chars=120)
            c1,c2,c3=st.columns(3)
            cantidad=campo_numero(c1, 'Cantidad',min_value=1,value=r.get('cantidad',1),step=1)
            largo=campo_numero(c2, 'Largo (m)',min_value=0.0,value=float(r.get('largo',0)),format='%.3f')
            ancho=campo_numero(c3, 'Ancho (m)',min_value=0.0,value=float(r.get('ancho',0)),format='%.3f')
            descuento=campo_numero(st, 'Superficie total a descontar (m²)',min_value=0.0,value=float(r.get('descuento',0)),format='%.3f',help='Solo exclusiones justificadas por el alcance; no descontar vanos de muros.')
            c1,c2=st.columns(2); calcular=c1.form_submit_button('Calcular',use_container_width=True); grabar=c2.form_submit_button('Calcular y guardar',type='primary',use_container_width=True)
            duplicar=st.form_submit_button('Guardar como copia',disabled=sel=='Nuevo')
        if calcular or grabar or duplicar:
            try:
                resultado=calcular_sector(nombre,cantidad,largo,ancho,descuento)
                st.success(f"Superficie neta: {resultado['neto']:.3f} m²")
                if grabar or duplicar:
                    from uuid import uuid4
                    datos['sectores'][str(uuid4()) if sel=='Nuevo' or duplicar else sel]=resultado; guardar(datos); st.rerun()
            except ValueError as e: st.error(str(e))
    elif vista=='Sectores guardados':
        titulo_seccion('01', 'Sectores guardados')
        st.table(a.set_index("Sector"))
        if datos['sectores']:
            k=st.selectbox('Sector',list(datos['sectores']),format_func=lambda k:datos['sectores'][k]['nombre'])
            confirm=st.checkbox('Confirmo la eliminación del sector')
            if st.button('Eliminar sector',disabled=not confirm,key='eliminar_sector_trazado'):
                del datos['sectores'][k]; guardar(datos); st.rerun()
    elif vista=='Memoria de cálculo':
        titulo_seccion('01', 'Memoria de cálculo')
        st.markdown('**Superficie neta = cantidad × largo × ancho − descuento total**')
        for r in datos['sectores'].values():
            st.write(f"{r['nombre']}: {r['cantidad']} × {r['largo']} × {r['ancho']} − {r['descuento']} = {r['neto']:.3f} m²")
        st.table(a.set_index("Sector"))
    elif vista=='Presupuesto y APU':
        titulo_seccion('01', 'Recursos y precios unitarios')
        st.caption('Ingresa consumo por m² y precio unitario de cada recurso según tu APU. Ejemplos: estacas, lienza, cal, mano de obra y nivel. No hay rendimientos predeterminados.')
        ids=list(datos['recursos']); k=st.selectbox('Recurso a editar',['Nuevo']+ids,format_func=lambda k:'Nuevo recurso' if k=='Nuevo' else datos['recursos'][k]['nombre'])
        r=datos['recursos'].get(k,{})
        with st.form(f'trazado_apu_{S.proyecto_id}_{k}'):
            tipos=['Material','Mano de obra','Equipo','Herramienta']; tipo=st.selectbox('Tipo',tipos,index=tipos.index(r.get('tipo','Material')))
            nombre=st.text_input('Recurso',r.get('nombre',''),max_chars=120); unidad=st.text_input('Unidad (un, ml, kg, h, etc.)',r.get('unidad',''),max_chars=20)
            c1,c2,c3=st.columns(3); consumo=campo_numero(c1, 'Consumo por m²',min_value=0.0,value=float(r.get('consumo',0)),format='%.5f'); precio=campo_numero(c2, 'Precio unitario ($)',min_value=0.0,value=float(r.get('precio',0))); perdida=campo_numero(c3, 'Pérdida / recargo (%)',min_value=0.0,value=float(r.get('perdida',0)))
            if st.form_submit_button('Guardar recurso',type='primary',use_container_width=True):
                nuevo=dict(tipo=tipo,nombre=nombre,unidad=unidad,consumo=consumo,precio=precio,perdida=perdida)
                try:
                    calcular_recursos(area,[nuevo]); from uuid import uuid4
                    datos['recursos'][str(uuid4()) if k=='Nuevo' else k]=nuevo; guardar(datos); st.rerun()
                except ValueError as e: st.error(str(e))
        if k!='Nuevo' and st.checkbox('Confirmar eliminación del recurso') and st.button('Eliminar recurso',key='eliminar_recurso_trazado'):
            del datos['recursos'][k]; guardar(datos); st.rerun()
        st.table(b.set_index("Recurso"))
        c1,c2=st.columns(2); c1.metric('Precio unitario directo',f"$ {b['Costo por m² ($)'].sum():,.2f}"); c2.metric('Costo directo total',f"$ {b['Total ($)'].sum():,.2f}")
    elif vista=='Exportar':
        titulo_seccion('01', 'Exportar documentos')
        if not datos['sectores']: st.info('Guarda al menos un sector para exportar.')
        else:
            x,p=exportar(datos,S.proyecto_nombre)
            st.download_button('Descargar Excel',x,'trazado_y_niveles.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            st.download_button('Descargar PDF',p,'trazado_y_niveles.pdf','application/pdf')
    else:
        st.info('Control geométrico: dimensiones positivas, descuentos inferiores a la superficie bruta y recursos no negativos.')
        st.warning('Verifica alcance contractual, solapes, ejes, cotas y nivel de referencia en los planos. El módulo no realiza levantamiento topográfico ni certifica tolerancias o cumplimiento normativo.')
        if not datos['sectores']: st.info('No hay sectores guardados.')
        if not datos['recursos']: st.warning('APU pendiente de configurar.')
        st.table(a.set_index("Sector"))
