import hashlib, json, math
import pandas as pd
import streamlit as st
from servicios.estado import S
from servicios.base_datos import extras_leer,extras_guardar
from autoplan.lector import dxf,pdf
from autoplan.integracion import DESTINOS,preparar
from autoplan.visor import limites,sector,sin_duplicados,imagen_pdf

def mostrar():
    if st.button('← Volver a categorías',key='autoplan_volver',type='primary'):
        S.partida_seleccionada=None; st.rerun()
    st.header('CubiSmart AutoPlan')
    st.caption('Proyecto activo: '+S.proyecto_nombre+' · Lectura geométrica asistida, no reconocimiento constructivo autónomo.')
    archivo=st.file_uploader('Importar plano',type=['dxf','dwg','pdf'],key='autoplan_archivo')
    if not archivo: return
    datos=archivo.getvalue(); ext=archivo.name.rsplit('.',1)[-1].lower(); huella=hashlib.sha256(datos).hexdigest()
    if len(datos)>30*1024*1024: st.error('Máximo 30 MB.'); return
    pagina=0
    try:
        if ext=='pdf':
            import fitz
            with fitz.open(stream=datos,filetype='pdf') as doc: n=len(doc)
            pagina=int(st.number_input('Página del plano',min_value=1,max_value=n,value=1))-1
        llave=(S.proyecto_id,huella,pagina,ext)
        if S.get('autoplan_cache_key')!=llave:
            if ext=='pdf':
                filas,omitidos,imagen=pdf(datos,pagina); unidad=None
            else:
                filas,unidad,omitidos=dxf(datos,ext); imagen=None
            S.autoplan_cache_key=llave; S.autoplan_cache=(filas,unidad,omitidos,imagen)
        filas,unidad,omitidos,imagen=S.autoplan_cache
    except Exception as e: st.error('No se pudo leer el plano: '+str(e)); return
    if not filas: st.warning('No se encontraron entidades compatibles. Los PDF escaneados requieren vectorización; no se aplica OCR.'); return
    st.caption(f'{len(filas)} entidades compatibles. Omitidas: {omitidos or "ninguna"}.')
    st.subheader('01 · Elegir zona del plano')
    if imagen: st.image(imagen,caption='Lámina original: ubica la planta o detalle que deseas medir')
    capas=sorted({r['capa'] for r in filas})
    suf=huella[:16]+str(pagina)
    filtro=st.multiselect('Capas a mostrar y medir',capas,default=capas,key='capas_'+suf)
    tipos=sorted({r['tipo'] for r in filas})
    tipos_sel=st.multiselect('Tipos de entidad',tipos,default=tipos,key='tipos_'+suf)
    base=[r for r in filas if r['capa'] in filtro and r['tipo'] in tipos_sel]
    if not base: st.info('Selecciona al menos una capa y tipo.'); return
    if ext=='pdf':
        import fitz
        with fitz.open(stream=datos,filetype='pdf') as doc:
            p=doc[pagina].rect; bounds=(p.x0,p.x1,p.y0,p.y1)
    else: bounds=limites(filas)
    x0,x1,y0,y1=bounds
    st.caption('Selecciona una sola planta o detalle. Las entidades que cruzan el límite se excluyen por completo de la medición.')
    if x1>x0: xr=st.slider('Sector horizontal X',float(x0),float(x1),(float(x0),float(x1)),key='x_'+suf,format='%.3f')
    else: xr=(x0,x1)
    if y1>y0: yr=st.slider('Sector vertical Y',float(y0),float(y1),(float(y0),float(y1)),key='y_'+suf,format='%.3f')
    else: yr=(y0,y1)
    caja=(*xr,*yr)
    if xr[0]==xr[1] or yr[0]==yr[1]:
        if ext=='pdf': st.warning('Selecciona una zona con superficie positiva.'); return
    visibles=sector(base,caja)
    if st.checkbox('Excluir duplicados geométricos exactos de la misma capa',value=False,key='dedup_'+suf):
        antes=len(visibles); visibles=sin_duplicados(visibles); st.caption(f'{antes-len(visibles)} duplicados excluidos. No se eliminan líneas paralelas ni superposiciones parciales.')
    if not visibles: st.warning('No hay entidades completas en el sector. Amplía los límites.'); return
    st.caption(f'{len(visibles)} entidades en la zona elegida.')
    if ext=='pdf': st.image(imagen_pdf(datos,pagina,caja),caption='Detalle original del sector, con textos y cotas')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    fig,ax=plt.subplots(figsize=(11,7))
    pal=plt.get_cmap('tab20'); colores={c:pal(i%20) for i,c in enumerate(capas)}
    lineas=[]; cs=[]; px=[]; py=[]
    for r in visibles:
        p=r['puntos']+([r['puntos'][0]] if r['cerrado'] else [])
        if len(p)>1: lineas.append(p); cs.append(colores[r['capa']] if ext!='pdf' else '#127566')
        else: px.append(p[0][0]); py.append(p[0][1])
    ax.add_collection(LineCollection(lineas,colors=cs,linewidths=.6))
    if px: ax.scatter(px,py,s=5,color='#127566')
    ax.autoscale(); ax.set_aspect('equal'); ax.grid(alpha=.12)
    if xr[0]<xr[1]: ax.set_xlim(*xr)
    if yr[0]<yr[1]: ax.set_ylim(*yr)
    if ext=='pdf': ax.invert_yaxis()
    if len(visibles)<=100:
        for r in visibles:
            x,y=r['puntos'][0]; ax.annotate(r['id'],(x,y),fontsize=6)
    st.pyplot(fig); plt.close(fig)
    st.subheader('02 · Confirmar escala del sector')
    if ext=='pdf':
        st.info('Calibra cada sector por separado. Una lámina puede contener varias escalas; no mezcles plantas y detalles.')
        referencias=[r for r in visibles if r['tipo']=='LINE' and r['longitud']>0]
        if not referencias: st.warning('No hay líneas para calibrar.'); return
        ref=st.selectbox('Línea de referencia (ID y longitud en puntos PDF)',referencias,key='ref_'+suf,format_func=lambda r:f"{r['id']} · {r['longitud']:.2f} pt · {r['puntos']}")
        fig,ax=plt.subplots(figsize=(10,6)); ax.add_collection(LineCollection(lineas,colors='#9DBBB0',linewidths=.6)); x,y=zip(*ref['puntos']); ax.plot(x,y,color='#B64242',linewidth=2); ax.set_aspect('equal'); ax.set_xlim(*xr); ax.set_ylim(yr[1],yr[0]); st.pyplot(fig); plt.close(fig)
        real=st.number_input('Longitud real de esa línea (m)',min_value=0.,value=None,placeholder='—',format='%.4f',key='real_'+suf+str(ref['id']))
        if not real: return
        factor=real/ref['longitud']
    else:
        st.caption('Unidad declarada por CAD: '+(f'{unidad} m por unidad' if unidad else 'No definida'))
        u=st.selectbox('Confirma unidad del dibujo',['Seleccionar','mm','cm','m','pulgadas','pies'],index=0,key='unidad_'+suf)
        if u=='Seleccionar': return
        factor={'mm':.001,'cm':.01,'m':1.,'pulgadas':.0254,'pies':.3048}[u]
    tabla=pd.DataFrame([{'ID':r['id'],'Capa':r['capa'],'Tipo':r['tipo'],'Bloque':r['bloque'],'Longitud (m)':r['longitud']*factor,'Área geométrica (m²)':r['area']*factor**2,'Rectángulo':r['rect']} for r in visibles])
    st.dataframe(tabla,use_container_width=True,hide_index=True)
    st.download_button('Descargar mediciones CSV',tabla.assign(**{k:tabla[k].map(lambda x: "'"+x if isinstance(x,str) and x.startswith(('=','+','-','@','\t','\r')) else x) for k in ('ID','Capa','Tipo','Bloque')}).to_csv(index=False).encode('utf-8-sig'),'mediciones_autoplan.csv','text/csv')
    st.subheader('Transferir a una partida')
    codigo=st.selectbox('Partida de destino',list(DESTINOS),format_func=lambda c:c+' · '+DESTINOS[c])
    opciones=[r for r in visibles if (r['rect'] if codigo in ('1.1','4.4','4.6') else r['tipo']=='INSERT' if codigo in ('5.1','5.4') else r['longitud']>0 and r['tipo']!='INSERT')]
    seleccion=st.multiselect('Entidades confirmadas',opciones,format_func=lambda r:f"{r['id']} · {r['capa']} · {r['bloque'] or r['tipo']}")
    especificacion=st.text_input('Especificación o material según plano (opcional)')
    st.warning('Confirma que las entidades corresponden a esta partida, que no se superponen y que la escala es correcta. Las líneas dobles, cotas, marcos y símbolos pueden no representar cantidades de obra.')
    confirmar=st.checkbox('Confirmo clasificación, escala y ausencia de duplicados geométricos.')
    if st.button('Guardar en partida',type='primary',disabled=not seleccion or not confirmar):
        try:
            e=extras_leer(S.proyecto_id); count=0
            for r in seleccion:
                nombre=f'AutoPlan {archivo.name[:45]} p{pagina+1} · {r["id"]}'
                grupo,coleccion,registro=preparar(r,codigo,factor,nombre,especificacion)
                destino=e.setdefault(grupo,{coleccion:{},'recursos':{}})
                rid='autoplan_'+hashlib.sha256(f'{huella}:{pagina}:{r["id"]}:{codigo}'.encode()).hexdigest()[:32]
                if rid in destino[coleccion]: continue
                destino[coleccion][rid]=registro; count+=1
            extras_guardar(S.proyecto_id,e); st.success(f'{count} registros nuevos guardados. Los ya importados se omitieron.')
        except Exception as e: st.error(str(e))
