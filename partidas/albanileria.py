"""CubiSmart: partidas.albanileria."""
from partidas.calculos_albanileria import calcular_muro
from servicios.estado import S
import math
import pandas as pd
import streamlit as st
from servicios.campos import numero as campo_numero

def mostrar_memoria():
    r = st.session_state.resultados
    st.markdown("## 📋 Memoria de cálculo detallada")
    if r.get('memoria'):
        st.caption('Muro: ' + (S.muro_en_edicion or S.dato_nombre_muro))
    if not r.get("memoria"):
        st.info("Realiza una cubicación para visualizar la memoria de cálculo.")
    else:
        m = r["memoria"]
        st.caption("Desarrollo de la última cubicación realizada. Todas las dimensiones se expresan en metros.")

        def paso(numero, titulo, formula, operacion, resultado):
            st.markdown(f"### {numero}. {titulo}")
            explicaciones = {1: ('Multiplica largo por altura, sin descontar aberturas.', 'Sb: superficie bruta; L: largo; H: altura.'), 3: ('Suma las superficies de puertas y ventanas.', 'Svt: superficie total de vanos; Σ: suma; n: número de vanos; Svi: superficie de cada vano.'), 4: ('Resta las aberturas al área total.', 'Sn: superficie neta; Sb: bruta; Svt: vanos.'), 5: ('Multiplica el área neta por el espesor.', 'Vm: volumen del muro; Sn: superficie neta; e: espesor.'), 7: ('Calcula el espacio de un ladrillo con sus juntas.', 'Smod: superficie modular; Lmod: largo modular; Hmod: alto modular.'), 8: ('Divide el área neta por el área de un ladrillo con juntas.', 'Nl: cantidad teórica; Sn: superficie neta; Smod: superficie modular.'), 9: ('Agrega unidades por cortes y desperdicios; redondea hacia arriba.', 'Nf: cantidad con pérdidas; Nl: cantidad teórica; Pl: pérdida porcentual.'), 10: ('Multiplica las tres dimensiones exteriores del ladrillo.', 'Vl: volumen exterior; Ll: largo; Hl: alto; Al: ancho.'), 11: ('Calcula el volumen de un ladrillo con sus juntas.', 'Vmod: volumen modular; Lmod: largo modular; Hmod: alto modular; Al: ancho.'), 12: ('Resta el volumen exterior del ladrillo al volumen modular.', 'Vmp: mortero por módulo; Vmod: volumen modular; Vl: volumen exterior.'), 13: ('Multiplica el mortero por módulo por el número teórico de ladrillos.', 'Vmt: mortero total; Vmp: mortero por módulo; Nl: cantidad teórica.'), 14: ('Agrega el porcentaje de desperdicio de mortero.', 'Vmf: mortero con pérdidas; Vmt: mortero total; Pm: pérdida porcentual.'), 15: ('Cada metro cúbico equivale a mil litros.', 'Vmf: volumen de mortero con pérdidas en m³.')}
            explicacion, variables = explicaciones[numero]
            st.write(explicacion)
            st.latex(formula)
            st.caption(variables)
            if numero == 3:
                st.write("En simple: vano 1 + vano 2 + los demás vanos.")
            st.latex(operacion)
            st.success(f"Resultado: {resultado}")
            st.divider()

        paso(1, "Superficie bruta del muro", r"S_b=L\times H",
             rf"S_b={m['largo']:.3f}\times {m['alto']:.3f}",
             f"{r['superficie']:.4f} m²")

        st.markdown("### 2. Superficie individual de vanos")
        st.write("Multiplica el ancho de cada abertura por su altura.")
        st.latex(r"S_v=A_v\times H_v")
        st.caption("Sv: superficie del vano; Av: ancho; Hv: altura.")
        if m["vanos"]:
            for i, (ancho, altura) in enumerate(m["vanos"], 1):
                st.markdown(f"**Vano {i}**")
                st.latex(rf"S_{{v{i}}}={ancho:.3f}\times {altura:.3f}")
                st.write(f"Resultado: {ancho * altura:.4f} m²")
        else:
            st.write("El muro no presenta vanos.")
        st.divider()

        suma = " + ".join(f"{a:.4f}" for a in r["detalle_vanos"]) or "0"
        paso(3, "Superficie total de vanos", r"S_{vt}=\sum_{i=1}^{n} S_{vi}",
             rf"S_{{vt}}={suma}", f"{r['superficie_vanos']:.4f} m²")
        paso(4, "Superficie neta del muro", r"S_n=S_b-S_{vt}",
             rf"S_n={r['superficie']:.4f}-{r['superficie_vanos']:.4f}", f"{r['superficie_neta']:.4f} m²")
        paso(5, "Volumen neto del muro", r"V_m=S_n\times e",
             rf"V_m={r['superficie_neta']:.4f}\times {m['espesor']:.3f}", f"{r['volumen']:.6f} m³")

        st.markdown("### 6. Dimensiones modulares del ladrillo")
        st.write("Suma el espesor de la junta al largo y alto del ladrillo.")
        st.caption("Lmod y Hmod: dimensiones modulares; Ll y Hl: dimensiones reales; J: junta.")
        st.latex(r"L_{mod}=L_l+J")
        st.latex(rf"L_{{mod}}={m['largo_ladrillo']:.3f}+{m['junta_mortero']:.3f}={m['largo_modular']:.3f}")
        st.latex(r"H_{mod}=H_l+J")
        st.latex(rf"H_{{mod}}={m['alto_ladrillo']:.3f}+{m['junta_mortero']:.3f}={m['alto_modular']:.3f}")
        st.divider()

        paso(7, "Superficie modular del ladrillo", r"S_{mod}=L_{mod}\times H_{mod}",
             rf"S_{{mod}}={m['largo_modular']:.3f}\times {m['alto_modular']:.3f}", f"{r['superficie_modular']:.6f} m²")
        paso(8, "Cantidad teórica de ladrillos", r"N_l=\frac{S_n}{S_{mod}}",
             rf"N_l=\frac{{{r['superficie_neta']:.4f}}}{{{r['superficie_modular']:.6f}}}",
             f"{m['cantidad_ladrillos']:.4f} unidades; redondeado hacia arriba: {r['ladrillos']} unidades")
        paso(9, "Ladrillos con pérdidas", r"N_f=N_l\times(1+P_l/100)",
             rf"N_f={m['cantidad_ladrillos']:.4f}\times(1+{m['porcentaje_perdida']:.2f}/100)",
             f"{m['cantidad_con_perdida']:.4f} unidades; redondeado hacia arriba: {r['ladrillos_finales']} unidades")
        paso(10, "Volumen individual del ladrillo", r"V_l=L_l\times H_l\times A_l",
             rf"V_l={m['largo_ladrillo']:.3f}\times {m['alto_ladrillo']:.3f}\times {m['ancho_ladrillo']:.3f}", f"{m['volumen_ladrillo']:.8f} m³")
        paso(11, "Volumen modular", r"V_{mod}=L_{mod}\times H_{mod}\times A_l",
             rf"V_{{mod}}={m['largo_modular']:.3f}\times {m['alto_modular']:.3f}\times {m['ancho_ladrillo']:.3f}", f"{m['volumen_modular']:.8f} m³")
        paso(12, "Mortero por módulo", r"V_{mp}=V_{mod}-V_l",
             rf"V_{{mp}}={m['volumen_modular']:.8f}-{m['volumen_ladrillo']:.8f}", f"{m['mortero_por_modulo']:.8f} m³")
        paso(13, "Mortero total", r"V_{mt}=V_{mp}\times N_l",
             rf"V_{{mt}}={m['mortero_por_modulo']:.8f}\times {m['cantidad_ladrillos']:.4f}", f"{r['mortero']:.6f} m³")
        paso(14, "Mortero con pérdidas", r"V_{mf}=V_{mt}\times(1+P_m/100)",
             rf"V_{{mf}}={r['mortero']:.6f}\times(1+{m['porcentaje_perdida_mortero']:.2f}/100)", f"{r['mortero_final']:.6f} m³")
        paso(15, "Conversión a litros", r"Litros=V_{mf}\times1000",
             rf"Litros={r['mortero_final']:.6f}\times1000", f"{r['mortero_final']*1000:.2f} L")

        st.markdown("### 📊 Resumen de materiales")
        st.table({
            "Material o elemento": ["Superficie neta", "Volumen neto", "Ladrillos sin pérdidas", "Ladrillos con pérdidas", "Mortero sin pérdidas", "Mortero con pérdidas", "Mortero equivalente"],
            "Cantidad": [f"{r['superficie_neta']:.4f}", f"{r['volumen']:.6f}", str(r['ladrillos']), str(r['ladrillos_finales']), f"{r['mortero']:.6f}", f"{r['mortero_final']:.6f}", f"{r['mortero_final']*1000:.2f}"],
            "Unidad": ["m²", "m³", "un", "un", "m³", "m³", "L"]
        })
        st.caption("Los valores de las fórmulas se redondean para su visualización; los cálculos usan los datos originales y el redondeo final del modelo.")
        st.info("Estimación geométrica simplificada. No incorpora criterios normativos de descuento, superposición de vanos ni relleno de perforaciones.")


def titulo_seccion(numero, nombre):
    st.markdown(
        f'''
        <div class="section-heading">
            <div class="section-number">{numero}</div>
            <div class="section-title">{nombre}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )


def mostrar_formulario():
    # ==========================================
    # 6. DIMENSIONES DEL MURO
    # ==========================================

    titulo_seccion("01", "Dimensiones del muro")

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            largo = campo_numero(st, 
                "Largo del muro (m)",
                min_value=0.0,
                step=0.1,
                format="%.2f",
                key="dato_largo_muro"
            )

        with col2:
            alto = campo_numero(st, 
                "Alto del muro (m)",
                min_value=0.0,
                step=0.1,
                format="%.2f",
                key="dato_alto_muro"
            )

        st.caption(
            "Introduce las dimensiones generales del muro en metros."
        )


    # ==========================================
    # 7. VANOS DEL MURO
    # ==========================================

    titulo_seccion("02", "Vanos del muro")

    with st.container(border=True):

        cantidad_vanos = campo_numero(st, 
            "Cantidad de vanos",
            min_value=0,
            max_value=30,
            step=1,
            key="dato_cantidad_vanos"
        )

        st.caption(
            "Considera puertas, ventanas y otras aberturas."
        )

        vanos = []

        for numero in range(cantidad_vanos):

            st.markdown(f"#### Vano {numero + 1}")

            col1, col2 = st.columns(2)

            with col1:
                ancho_vano = campo_numero(st, 
                    f"Ancho del vano {numero + 1} (m)",
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    key=f"dato_ancho_vano_{numero}"
                )

            with col2:
                alto_vano = campo_numero(st, 
                    f"Alto del vano {numero + 1} (m)",
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    key=f"dato_alto_vano_{numero}"
                )

            vanos.append((ancho_vano, alto_vano))


    # ==========================================
    # 8. CARACTERISTICAS DEL LADRILLO
    # ==========================================

    titulo_seccion("03", "Características del ladrillo")


    with st.container(border=True):

        st.markdown(
            """
            <div class="aviso-ladrillo">
                Ingresa el largo y el alto de la cara visible
                del ladrillo. El ancho corresponde al espesor
                del muro en este modelo simplificado.
            </div>
            """,
            unsafe_allow_html=True
        )


        col1, col2, col3 = st.columns(3)

        with col1:
            largo_ladrillo = campo_numero(st, 
                "Largo (m)",
                min_value=0.0,
                step=0.01,
                format="%.3f",
                key="dato_largo_ladrillo"
            )

        with col2:
            alto_ladrillo = campo_numero(st, 
                "Alto (m)",
                min_value=0.0,
                step=0.01,
                format="%.3f",
                key="dato_alto_ladrillo"
            )

        with col3:
            ancho_ladrillo = campo_numero(st, 
                "Ancho (m)",
                min_value=0.0,
                step=0.01,
                format="%.3f",
                key="dato_ancho_ladrillo"
            )

        junta_mortero = campo_numero(st, 
            "Espesor de junta de mortero (m)",
            min_value=0.0,
            step=0.005,
            format="%.3f",
            key="dato_junta_mortero"
        )

        st.caption(
            "Ejemplo: una junta de 1 cm equivale a 0.01 m."
        )


    # ==========================================
    # 9. PORCENTAJES DE PERDIDA
    # ==========================================

    titulo_seccion("04", "Porcentajes de pérdida")

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            porcentaje_perdida = campo_numero(st, 
                "Pérdida de ladrillos (%)",
                min_value=0.0,
                step=1.0,
                format="%.1f",
                key="dato_perdida_ladrillos"
            )

        with col2:
            porcentaje_perdida_mortero = campo_numero(st, 
                "Pérdida de mortero (%)",
                min_value=0.0,
                step=1.0,
                format="%.1f",
                key="dato_perdida_mortero"
            )

        st.caption(
            "Introduce los porcentajes de pérdida "
            "que deseas considerar en el cálculo."
        )


def mostrar_resultados():
    r = st.session_state.resultados

    st.divider()

    st.markdown("## 📊 Resultados de cubicación")
    if r.get("memoria"):
        st.caption("Resultados de la última cubicación realizada. Si cambias algún dato, vuelve a calcular.")

    # SUPERFICIES

    st.markdown("### 📐 Superficies del muro")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Superficie total",
            f"{r['superficie']:.2f} m²"
        )

        st.metric(
            "Superficie de vanos",
            f"{r['superficie_vanos']:.2f} m²"
        )

    with col2:
        st.metric(
            "Superficie neta",
            f"{r['superficie_neta']:.2f} m²"
        )

        st.metric(
            "Volumen del muro",
            f"{r['volumen']:.3f} m³"
        )


    # DETALLE DE VANOS

    if r["detalle_vanos"]:

        with st.expander("Ver detalle de vanos"):

            for numero, superficie_vano in enumerate(
                r["detalle_vanos"]
            ):
                st.write(
                    f"Vano {numero + 1}: "
                    f"{superficie_vano:.2f} m²"
                )


    # RESULTADOS DE LADRILLOS

    st.divider()

    st.markdown("### 🧱 Cantidad de ladrillos")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Cantidad teórica",
            f"{r['ladrillos']} unidades"
        )

    with col2:
        st.metric(
            "Cantidad con pérdidas",
            f"{r['ladrillos_finales']} unidades"
        )

    st.caption(
        f"Superficie modular del ladrillo: "
        f"{r['superficie_modular']:.4f} m²"
    )


    # RESULTADOS DE MORTERO

    st.divider()

    st.markdown("### 🪣 Mortero de pega")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Mortero teórico",
            f"{r['mortero']:.4f} m³"
        )

    with col2:
        st.metric(
            "Mortero con pérdidas",
            f"{r['mortero_final']:.4f} m³"
        )

    st.caption(
        f"Volumen equivalente con pérdidas: "
        f"{r['mortero_final'] * 1000:.2f} litros"
    )


def mostrar_muros():
    st.markdown('## 📁 Muros guardados')
    st.caption('Proyecto: '+S.proyecto_nombre)
    muros=S.muros_guardados
    if not muros:
        st.info('Todavía no hay muros guardados.'); return
    campos=[('Superficie bruta (m²)','superficie',2),('Vanos (m²)','superficie_vanos',2),('Superficie neta (m²)','superficie_neta',2),('Volumen (m³)','volumen',3),('Ladrillos (un)','ladrillos_finales',0),('Mortero (m³)','mortero_final',4)]
    filas=[dict({'Muro':n},**{titulo:f'{r[k]:.{p}f}' for titulo,k,p in campos}) for n,r in muros.items()]
    filas.append(dict({'Muro':'TOTAL'},**{titulo:f'{sum(r[k] for r in muros.values()):.{p}f}' for titulo,k,p in campos}))
    df=pd.DataFrame(filas)
    st.dataframe(df.style.apply(lambda fila: ['background-color: #127566; color: white; font-weight: bold' if fila.name==len(df)-1 else 'background-color: #F5F9F7; color: #163B39']*len(fila),axis=1),hide_index=True,use_container_width=True)
    st.caption('Totales calculados antes del redondeo de visualización. Ladrillos redondeados por muro.')


def mostrar_resumen():
    st.markdown('## 📊 Resumen general del proyecto')
    st.caption('Proyecto: '+S.proyecto_nombre)
    muros=S.muros_guardados
    campos=[('Superficie bruta total','superficie',2,'m²'),('Vanos totales','superficie_vanos',2,'m²'),('Superficie neta total','superficie_neta',2,'m²'),('Volumen total','volumen',3,'m³'),('Ladrillos con pérdidas','ladrillos_finales',0,'un'),('Mortero con pérdidas','mortero_final',4,'m³')]
    st.metric('Muros guardados',len(muros))
    cols=st.columns(2)
    for i,(t,k,p,u) in enumerate(campos): cols[i%2].metric(t,f'{sum(r[k] for r in muros.values()):.{p}f} {u}')
    st.caption('El volumen total de mortero no distingue dosificaciones. Si utilizas distintos tipos de ladrillo, verifica las cantidades de cada muro antes de comprar.')


def mostrar_dosificacion():
    st.markdown('## 🪣 Dosificación de mortero')
    v=S.resultados.get('mortero_final',0.)
    if v<=0:
        st.info('Calcula o carga un muro con mortero para continuar.'); return
    st.caption('Dosificación del muro actualmente calculado o cargado; incluye pérdidas.')
    st.metric('Mortero requerido',f'{v:.4f} m³ · {v*1000:.2f} L')
    tipo=st.radio('Preparación',['Preparado en obra','Mortero premezclado'],key='dos_tipo',horizontal=True)
    def num(t,k,val,minimo,step):
        if k not in S: S[k]=val
        return campo_numero(st, t,min_value=minimo,step=step,key=k)
    def paso(t,exp,f,op,res):
        st.markdown('#### '+t); st.write(exp); st.latex(f); st.latex(op); st.success(res)
    a,b=st.columns(2)
    if tipo=='Preparado en obra':
        with a:
            pc=num('Partes de cemento','dos_pc',1.,.1,.5)
            fs=num('Factor de volumen seco','dos_fs',1.33,1.,.01)
            dc=num('Densidad aparente cemento (kg/m³)','dos_dc',1440.,1.,10.)
        with b:
            pa=num('Partes de arena','dos_pa',4.,.1,.5)
            ps=num('Peso saco cemento (kg)','dos_ps',25.,1.,1.)
            rac=num('Relación agua/cemento','dos_rac',.6,0.,.05)
        vs=v*fs; pt=pc+pa; vc=vs*pc/pt; va=vs*pa/pt; c=vc*dc; n=c/ps; sacos=math.ceil(round(n,9)); agua=c*rac
        a,b=st.columns(2); a.metric('Cemento',f'{c:.2f} kg'); b.metric('Sacos para compra',sacos); a.metric('Arena',f'{va:.4f} m³'); b.metric('Agua estimada',f'{agua:.2f} L')
        st.info('Parámetros referenciales, no una dosificación certificada. Ajusta agua por humedad y trabajabilidad; usa la especificación de obra.')
        with st.expander('📋 Memoria de dosificación'):
            for t,exp,f,op,res in [
                ('Volumen seco','Multiplica el mortero por el factor seco.',r'V_s=V_m F_s',f'{v:.6f} × {fs:g}',f'{vs:.6f} m³'),
                ('Partes totales','Suma las partes de cemento y arena.',r'P_t=P_c+P_a',f'{pc:g}+{pa:g}',f'{pt:g} partes'),
                ('Volumen de cemento','Distribuye el volumen seco según la proporción de cemento.',r'V_c=V_s P_c/P_t',f'{vs:.6f} × {pc:g}/{pt:g}',f'{vc:.6f} m³'),
                ('Cemento en kg','Multiplica el volumen por la densidad aparente.',r'C=V_c D_c',f'{vc:.6f} × {dc:g}',f'{c:.2f} kg'),
                ('Sacos','Divide la masa por el peso del saco y redondea hacia arriba.',r'N=C/P_s',f'{c:.4f}/{ps:g}',f'{n:.4f} teóricos; {sacos} para compra'),
                ('Arena','Distribuye el volumen seco según la proporción de arena.',r'V_a=V_s P_a/P_t',f'{vs:.6f} × {pa:g}/{pt:g}',f'{va:.6f} m³'),
                ('Agua','Multiplica cemento por relación agua/cemento.',r'A=C R_{ac}',f'{c:.4f} × {rac:g}',f'{agua:.2f} L')]: paso(t,exp,f,op,res)
    else:
        with a: ps=num('Peso saco (kg)','dos_pre_peso',25.,1.,1.)
        with b: rend=num('Rendimiento por saco (L)','dos_pre_rend',15.,.1,.5)
        litros=v*1000; n=litros/rend; sacos=math.ceil(round(n,9)); rt=sacos*rend
        a.metric('Sacos necesarios',sacos); b.metric('Peso compra',f'{sacos*ps:.2f} kg'); a.metric('Rendimiento total',f'{rt:.2f} L'); b.metric('Excedente',f'{max(0,rt-litros):.2f} L')
        st.info('Usa rendimiento y agua de amasado de la ficha técnica del fabricante.')
        with st.expander('📋 Memoria de dosificación'):
            paso('Litros','Convierte metros cúbicos a litros.',r'V_L=V_m × 1000',f'{v:.6f} × 1000',f'{litros:.2f} L')
            paso('Sacos','Divide por rendimiento y redondea hacia arriba.',r'N=V_L/R_s',f'{litros:.4f}/{rend:g}',f'{n:.4f} teóricos; {sacos} para compra')
            paso('Peso','Multiplica sacos por su peso.',r'P=N P_s',f'{sacos} × {ps:g}',f'{sacos*ps:.2f} kg')
            paso('Rendimiento','Multiplica sacos por rendimiento.',r'R=N R_s',f'{sacos} × {rend:g}',f'{rt:.2f} L')
            paso('Excedente','Resta el volumen necesario al rendimiento.',r'E=R-V_L',f'{rt:.4f}-{litros:.4f}',f'{max(0,rt-litros):.2f} L')


def control_tecnico():
    st.header('Control técnico de cubicación')
    st.warning('Método geométrico simplificado. No acredita NCh353 ni reemplaza revisión profesional. No incluye confinamientos, aparejos especiales, superposición de vanos ni rellenos.')
    filas=[]
    for n,r in S.muros_guardados.items():
        try:
            rr=calcular_muro(r['datos']); ok=all(math.isclose(rr[k],r[k],rel_tol=1e-9,abs_tol=1e-9) for k in ('superficie','superficie_neta','volumen','ladrillos_finales','mortero_final')); estado='Coincide' if ok else 'Revisar'
        except (ValueError,KeyError,TypeError,OverflowError): estado='Datos inválidos'
        filas.append({'Muro':n,'Recalculo interno':estado})
    st.dataframe(pd.DataFrame(filas),hide_index=True)
    st.caption('Esta comprobación verifica coherencia interna, no es validación independiente. Contrasta planos, mediciones manuales y especificaciones de obra.')


