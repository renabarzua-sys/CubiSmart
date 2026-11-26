"""CubiSmart: servicios.presupuestos."""
from servicios.base_datos import extras_guardar
from servicios.base_datos import extras_leer
from servicios.estado import S
from servicios.exportaciones import costos_exportar
import math
import pandas as pd
import streamlit as st
from servicios.campos import numero as campo_numero

P_DEFAULT={'tipo':'En obra','pa':4.,'fs':1.33,'dc':1440.,'ps':25.,'rac':.6,'rend':15.}

def cantidades_presupuesto(muros, p):
    grupos={}
    for r in muros.values():
        m=r['memoria']; dim=tuple(m[k] for k in ('largo_ladrillo','alto_ladrillo','ancho_ladrillo'))
        grupos[dim]=grupos.get(dim,0)+r['ladrillos_finales']
    filas=[('Ladrillo '+ ' × '.join(f'{x*100:g}' for x in dim)+' cm','un',q) for dim,q in grupos.items()]
    v=sum(r['mortero_final'] for r in muros.values())
    if p['tipo']=='Premezclado':
        filas.append(('Mortero premezclado','saco',math.ceil(round(v*1000/p['rend'],9))))
    else:
        seco=v*p['fs']; c=seco/(1+p['pa'])*p['dc']; arena=seco*p['pa']/(1+p['pa'])
        filas.extend([('Cemento','saco',math.ceil(round(c/p['ps'],9))),('Arena','m³',arena),('Agua estimada','L',c*p['rac'])])
    return filas


def mostrar_costos(apu=False):
    st.header('Análisis de precios unitarios (APU)' if apu else 'Presupuesto de materiales')
    muros=S.muros_guardados
    area=sum(r['superficie_neta'] for r in muros.values())
    if not muros or area<=0:
        st.info('Guarda al menos un muro.')
        return

    e=extras_leer(S.proyecto_id)
    p=dict(P_DEFAULT,**e.get('dosificacion',{}))
    pref=('apu' if apu else 'presupuesto')

    if not apu:
        with st.form('dos_proyecto_'+str(S.proyecto_id)):
            st.markdown('### Dosificación general del proyecto')
            tipo=st.radio('Preparación',['En obra','Premezclado'],index=int(p['tipo']=='Premezclado'),horizontal=True)
            st.caption('Parámetros referenciales para el presupuesto del proyecto.')
            c1,c2=st.columns(2)
            with c1:
                vals={}
                vals['tipo']=tipo
                vals['pa']=campo_numero(st, 'Partes arena',min_value=.1,value=float(p['pa']))
                vals['fs']=campo_numero(st, 'Factor seco',min_value=1.,value=float(p['fs']))
                vals['dc']=campo_numero(st, 'Densidad cemento kg/m³',min_value=1.,value=float(p['dc']))
            with c2:
                vals['ps']=campo_numero(st, 'Peso saco cemento kg',min_value=1.,value=float(p['ps']))
                vals['rac']=campo_numero(st, 'Relación agua/cemento',min_value=0.,value=float(p['rac']))
                vals['rend']=campo_numero(st, 'Rendimiento premezclado L/saco',min_value=.1,value=float(p['rend']))
            if st.form_submit_button('Guardar dosificación general',use_container_width=True,type='primary'):
                e['dosificacion']=vals
                extras_guardar(S.proyecto_id,e)
                st.rerun()

    base=cantidades_presupuesto(muros,p)
    precios=e.get('precios',{})
    a=e.get('apu',{})
    st.caption(f'Proyecto: {S.proyecto_nombre} · {area:.4f} m² netos · {p["tipo"]}. Precios netos en CLP; no incluye confinamiento.')

    with st.container(key='costos_panel'):
        with st.form(pref+'_form_'+str(S.proyecto_id)):
            st.markdown('### Materiales base')
            nuevos={}
            filas=[]
            for i,(nombre,u,q) in enumerate(base):
                cantidad=q/area if apu else q
                with st.container():
                    c1,c2=st.columns([1.15,1])
                    with c1:
                        st.markdown(f"**{nombre}**")
                        st.caption(f"Consumo: {cantidad:.4f} {u}" + (' por m²' if apu else ''))
                    with c2:
                        precio=campo_numero(st, 'Precio neto · '+nombre,min_value=0.,value=float(precios.get(nombre,0)),step=1.,key=f'{pref}_{S.proyecto_id}_{i}')
                nuevos[nombre]=precio
                filas.append((nombre,u,cantidad,precio,cantidad*precio))

            recursos={}
            if apu:
                st.markdown('### Mano de obra y equipos')
                for idx,(nombre,u) in enumerate([('Maestro albañil','HD'),('Ayudante','HD'),('Betonera','HD'),('Herramientas menores','gl')]):
                    old=a.get(nombre,[0.,0.])
                    c1,c2=st.columns(2)
                    with c1:
                        q=campo_numero(st, nombre+' · '+u+'/m²',min_value=0.,value=float(old[0]),format='%.4f',key=f'apuq_{S.proyecto_id}_{idx}')
                    with c2:
                        pr=campo_numero(st, 'Precio neto · '+nombre,min_value=0.,value=float(old[1]),step=1.,key=f'apup_{S.proyecto_id}_{idx}')
                    recursos[nombre]=[q,pr]
                    filas.append((nombre,u,q,pr,q*pr))

            iva_on=st.checkbox('Agregar IVA 19 %',value=bool(e.get(pref+'_iva',True)))
            if st.form_submit_button('Guardar y actualizar costos',use_container_width=True,type='primary'):
                e['precios']=nuevos
                e[pref+'_iva']=iva_on
                if apu:
                    e['apu']=recursos
                extras_guardar(S.proyecto_id,e)
                st.success('Costos guardados correctamente.')
                st.rerun()

    # Releer datos guardados para construir el resumen y evitar mostrar borradores.
    e=extras_leer(S.proyecto_id)
    precios=e.get('precios',{})
    a=e.get('apu',{})
    filas=[]
    for nombre,u,q in base:
        cantidad=q/area if apu else q
        precio=float(precios.get(nombre,0))
        filas.append((nombre,u,cantidad,precio,cantidad*precio))
    if apu:
        for nombre,u in [('Maestro albañil','HD'),('Ayudante','HD'),('Betonera','HD'),('Herramientas menores','gl')]:
            q,pr=a.get(nombre,[0.,0.])
            filas.append((nombre,u,float(q),float(pr),float(q)*float(pr)))
    iva_on=bool(e.get(pref+'_iva',True))
    subtotal=sum(f[4] for f in filas)
    iva=subtotal*.19 if iva_on else 0.
    total=subtotal+iva

    if any(f[2]>0 and f[3]==0 for f in filas):
        st.warning('Hay recursos con precio cero. Completa los precios antes de usar el presupuesto.')

    with st.container(key='costos_resultados'):
        st.markdown('### Resumen de costos')
        m1,m2,m3=st.columns(3)
        m1.metric('Subtotal neto'+(' por m²' if apu else ''),f'$ {subtotal:,.2f}')
        m2.metric('IVA (19 %)' if iva_on else 'IVA',f'$ {iva:,.2f}')
        m3.metric('Total'+(' por m²' if apu else ''),f'$ {total:,.2f}')
        tabla=pd.DataFrame(filas,columns=['Recurso','Unidad','Cantidad','Precio neto CLP','Total neto CLP'])
        tabla['Cantidad']=tabla['Cantidad'].map(lambda x: f'{x:,.4f}')
        tabla['Precio neto CLP']=tabla['Precio neto CLP'].map(lambda x: f'$ {x:,.2f}')
        tabla['Total neto CLP']=tabla['Total neto CLP'].map(lambda x: f'$ {x:,.2f}')
        st.table(tabla)
        if apu:
            st.caption(f'Costo directo neto del proyecto: $ {subtotal*area:,.2f}. No incluye gastos generales ni utilidad.')

    x,b=costos_exportar(('APU por m²' if apu else 'Presupuesto')+' | '+S.proyecto_nombre,filas,subtotal,iva,total)
    st.markdown('### Descargas')
    c1,c2=st.columns(2)
    c1.download_button('Descargar Excel',x,pref+'.xlsx',use_container_width=True)
    c2.download_button('Descargar PDF',b,pref+'.pdf',use_container_width=True)


