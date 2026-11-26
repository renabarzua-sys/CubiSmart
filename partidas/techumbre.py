"""Interfaz de techumbre y cubierta, independiente de las otras partidas."""
import streamlit as st
from servicios.campos import numero as campo_numero
import pandas as pd
from io import BytesIO
from uuid import uuid4
from xml.sax.saxutils import escape
from partidas.calculos_techumbre import CAT,CAMPOS,GUIA,calcular
from partidas.calculos_trazado import calcular_recursos
from partidas.albanileria import titulo_seccion
from servicios.estado import S
from servicios.base_datos import extras_leer,extras_guardar
from servicios.gestion_muros import volver_proyectos

def leer(c):
    return extras_leer(S.proyecto_id).get('techumbre_'+c,{'elementos':{},'recursos':{}})
def guardar(c,d):
    e=extras_leer(S.proyecto_id); e['techumbre_'+c]=d; extras_guardar(S.proyecto_id,e)
def tablas(c,d):
    u=CAT[c][1]; registros=[calcular(c,r['nombre'],r['cantidad'],r['valores'],r.get('especificacion')) for r in d['elementos'].values()]; total=sum(r['neto'] for r in registros)
    a=pd.DataFrame([{'Elemento':r['nombre'],'Cantidad de elementos':r['cantidad'],'Especificación':r['especificacion'],**{et:r['valores'][k] for k,et,_,_ in CAMPOS[c]},'Bruto':r['bruto'],f'Neto ({u})':r['neto'],**r['aux']} for r in registros])
    filas=calcular_recursos(total,list(d['recursos'].values()))
    b=pd.DataFrame(filas,columns=['tipo','nombre','unidad','consumo','perdida','precio','cantidad','costo_unitario','total']).rename(columns={'tipo':'Tipo','nombre':'Recurso','unidad':'Unidad','consumo':f'Consumo por {u}','perdida':'Recargo (%)','precio':'Precio ($)','cantidad':'Cantidad total','costo_unitario':'Costo unitario ($)','total':'Total ($)'})
    return total,a,b

def exportar(c,d,proyecto):
    t,a,b=tablas(c,d); n,u=CAT[c]; pu=float(b['Costo unitario ($)'].sum()); costo=float(b['Total ($)'].sum())
    resumen=pd.DataFrame([{'Proyecto':proyecto,'Ítem':c,'Partida':n,'Unidad':u,'Cantidad':t,'PU directo ($)':pu,'Total directo ($)':costo,'Fórmula':GUIA[c][1]}]); x=BytesIO()
    with pd.ExcelWriter(x,engine='xlsxwriter',engine_kwargs={'options':{'strings_to_formulas':False,'strings_to_urls':False}}) as w:
        for nombre,df in [('Resumen',resumen),('Memoria',a),('APU',b)]:
            df.to_excel(w,sheet_name=nombre,index=False); w.sheets[nombre].set_column(0,max(0,len(df.columns)-1),23)
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4,landscape
    p=BytesIO(); styles=getSampleStyleSheet(); story=[Paragraph(escape('CubiSmart | '+c+' '+n),styles['Title']),Paragraph(escape(proyecto),styles['Normal']),Paragraph(escape(f'Cantidad: {t:.3f} {u} | PU directo: $ {pu:,.2f} | Total: $ {costo:,.2f}'),styles['Normal']),Paragraph(escape(GUIA[c][1]),styles['Normal']),Spacer(1,12)]
    # Una ficha vertical por elemento para evitar tablas demasiado anchas.
    for _,r in a.iterrows():
        story.append(Paragraph(escape(str(r['Elemento'])),styles['Heading2']))
        for k,v in r.items():
            if k!='Elemento': story.append(Paragraph(escape(f'{k}: '+(f'{v:.5f}' if isinstance(v,float) else str(v))),styles['Normal']))
    story.append(Paragraph('Recursos y APU',styles['Heading2']))
    rows=[[Paragraph(escape(str(k)),styles['Normal']) for k in b.columns]]
    for r in b.itertuples(index=False,name=None): rows.append([Paragraph(escape(f'{v:.3f}' if isinstance(v,float) else str(v)),styles['Normal']) for v in r])
    table=Table(rows,repeatRows=1,colWidths=[735/len(b.columns)]*len(b.columns)); table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDF0E8')),('GRID',(0,0),(-1,-1),.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(table); SimpleDocTemplate(p,pagesize=landscape(A4),leftMargin=45,rightMargin=45).build(story)
    return x.getvalue(),p.getvalue()

def mostrar(c):
    nombre,u=CAT[c]; prefix='tech_'+c.replace('.','_')+'_'+str(S.proyecto_id); guia,formula,ejemplos=GUIA[c]
    with st.sidebar:
        st.markdown('## CubiSmart'); st.caption(c+' · '+nombre)
        if st.button('← Volver a elegir partida',key='og_volver',use_container_width=True): S.partida_seleccionada=None; st.rerun()
        st.button('Volver a mis proyectos',key='og_proyectos',on_click=volver_proyectos,use_container_width=True)
        st.divider(); st.markdown('### Navegación')
        vista=st.radio('Navegación',['Cubicación','Memoria de cálculo','Elementos guardados','Resumen general','Presupuesto','APU','Exportar','Control técnico'],key='navegacion_partida',label_visibility='collapsed',format_func=lambda v:'▸ '+v)
    with st.container(key='partida_panel'):
        st.markdown('### '+c+' · '+nombre); st.caption('Proyecto activo: '+S.proyecto_nombre+' · Unidad: '+u)
        d=leer(c); total,a,b=tablas(c,d); st.metric('Cantidad neta acumulada',f'{total:,.3f} {u}')
        if vista=='Cubicación':
            titulo_seccion('01','Datos del elemento'); st.info(guia); st.markdown('**'+formula+'**')
            sel=st.selectbox('Elemento a editar o duplicar',['Nuevo']+list(d['elementos']),format_func=lambda k:'Nuevo elemento' if k=='Nuevo' else d['elementos'][k]['nombre'],key=prefix+'_sel'); r=d['elementos'].get(sel,{})
            with st.form(prefix+'_form_'+sel):
                nom=st.text_input('Nombre del elemento / eje',r.get('nombre',''),max_chars=120); n=campo_numero(st, 'Cantidad de elementos iguales',min_value=1,step=1,value=r.get('cantidad',1)); v={}
                especificacion=st.text_input('Material, sección, espesor o modelo según proyecto',value=r.get('especificacion',''),max_chars=180)
                st.caption('No se impone un material ni dimensión comercial. Usa el producto y despiece especificados.')
                campos=CAMPOS[c]
                for i in range(0,len(campos),2):
                    for col,(k,et,defecto,_) in zip(st.columns(2),campos[i:i+2]):
                        v[k]=campo_numero(col, et,min_value=0.,value=float(r.get('valores',{}).get(k,defecto)),format='%.4f')
                c1,c2,c3=st.columns(3); calc=c1.form_submit_button('Calcular',use_container_width=True); save=c2.form_submit_button('Calcular y guardar',type='primary',use_container_width=True); dup=c3.form_submit_button('Guardar copia',disabled=sel=='Nuevo',use_container_width=True)
            if calc or save or dup:
                try:
                    res=calcular(c,nom,n,v,especificacion); st.success(f"Cantidad neta: {res['neto']:.3f} {u}")
                    for k,val in res['aux'].items(): st.metric(k,f'{val:.4f}')
                    if save or dup: d['elementos'][str(uuid4()) if sel=='Nuevo' or dup else sel]=res; guardar(c,d); st.rerun()
                except ValueError as e: st.error(str(e))
        elif vista in ('Memoria de cálculo','Elementos guardados','Resumen general','Control técnico'):
            titulo_seccion('01',vista)
            if vista=='Memoria de cálculo': st.markdown('**'+formula+'**')
            if vista=='Control técnico':
                st.warning('Cubicación geométrica, no diseño estructural. Verifica planos, especificaciones, descuentos y solapes. Los rendimientos y factores de compra deben justificarse.'); st.info(guia)
                if not d['recursos']: st.warning('APU aún sin recursos.')
            if not a.empty: st.table(a.set_index('Elemento'))
            else: st.info('No hay elementos guardados.')
            if vista=='Resumen general' and d['elementos']:
                aux={}
                for r in d['elementos'].values():
                    for k,v in r['aux'].items():
                        if k not in ('Ancho inclinado (m)','Unidades comerciales estimadas (un)'): aux[k]=aux.get(k,0)+v
                for k,v in aux.items(): st.metric(k,f'{v:.4f}')
                st.caption('Las unidades comerciales se estiman por registro; no se suman entre productos distintos. Revisa el despiece y reutilización de recortes.')
            if vista=='Elementos guardados' and d['elementos']:
                k=st.selectbox('Elemento',list(d['elementos']),format_func=lambda k:d['elementos'][k]['nombre'],key=prefix+'_del'); confirm=st.checkbox('Confirmo la eliminación',key=prefix+'_conf')
                if st.button('Eliminar elemento',key='og_eliminar_elemento',disabled=not confirm): del d['elementos'][k]; guardar(c,d); st.rerun()
        elif vista in ('Presupuesto','APU'):
            titulo_seccion('01',vista); st.caption('APU común a la partida. Si existen productos distintos, calcula consumos ponderados o recursos separados según sus cantidades. Recursos sugeridos: '+ejemplos+'. Ingresa consumos por '+u+'; no existen precios ni rendimientos predeterminados. Evita duplicar recargos de suministro o traslapos.')
            if vista=='APU':
                k=st.selectbox('Recurso a editar',['Nuevo']+list(d['recursos']),format_func=lambda k:'Nuevo recurso' if k=='Nuevo' else d['recursos'][k]['nombre'],key=prefix+'_rec'); r=d['recursos'].get(k,{})
                with st.form(prefix+'_apu_'+k):
                    tipos=['Material','Mano de obra','Equipo','Herramienta']; tipo=st.selectbox('Tipo',tipos,index=tipos.index(r.get('tipo','Material'))); nom=st.text_input('Recurso',r.get('nombre',''),max_chars=120); unidad=st.text_input('Unidad',r.get('unidad',''),max_chars=20); c1,c2,c3=st.columns(3); consumo=campo_numero(c1, 'Consumo por '+u,min_value=0.,value=float(r.get('consumo',0)),format='%.6f'); precio=campo_numero(c2, 'Precio unitario ($)',min_value=0.,value=float(r.get('precio',0))); perdida=campo_numero(c3, 'Recargo (%)',min_value=0.,value=float(r.get('perdida',0)))
                    if st.form_submit_button('Guardar recurso',type='primary',use_container_width=True):
                        nuevo=dict(tipo=tipo,nombre=nom,unidad=unidad,consumo=consumo,precio=precio,perdida=perdida)
                        try: calcular_recursos(total,[nuevo]); d['recursos'][str(uuid4()) if k=='Nuevo' else k]=nuevo; guardar(c,d); st.rerun()
                        except ValueError as e: st.error(str(e))
                if k!='Nuevo' and st.checkbox('Confirmar eliminación',key=prefix+'_recconf') and st.button('Eliminar recurso',key='og_eliminar_recurso'): del d['recursos'][k]; guardar(c,d); st.rerun()
            st.table(b.set_index('Recurso')); c1,c2=st.columns(2); c1.metric('Precio unitario directo',f"$ {b['Costo unitario ($)'].sum():,.2f}"); c2.metric('Costo directo total',f"$ {b['Total ($)'].sum():,.2f}")
        elif vista=='Exportar':
            titulo_seccion('01','Exportar documentos')
            if not d['elementos']: st.info('Guarda al menos un elemento.')
            else:
                x,p=exportar(c,d,S.proyecto_nombre); st.download_button('Descargar Excel',x,f'partida_{c}.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'); st.download_button('Descargar PDF',p,f'partida_{c}.pdf','application/pdf')
    st.markdown('<div class="footer">CubiSmart · Techumbre y cubierta</div>',unsafe_allow_html=True)
