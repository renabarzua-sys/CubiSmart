
import streamlit as st
import math

# ==========================================
# 1. CONFIGURACION GENERAL
# ==========================================

st.set_page_config(
    page_title="CubiMat | Cubicación de materiales",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. DISEÑO VISUAL
# ==========================================

st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 85% 5%, #D5EEE5 0%, transparent 35%),
            radial-gradient(circle at 5% 80%, #E2EFEC 0%, transparent 35%),
            linear-gradient(135deg, #F5F9F7, #E9F3EF);
        color: #163B39;
    }

    .block-container {
        max-width: 1100px;
        padding: 2rem 3rem 4rem;
    }

    h1, h2, h3 {
        color: #163B39 !important;
        letter-spacing: -0.5px;
    }

    .hero {
        background: linear-gradient(115deg, #124F49, #208C79);
        border-radius: 24px;
        padding: 35px 38px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 15px 35px rgba(15, 87, 73, 0.20);
        position: relative;
        overflow: hidden;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -50px;
        top: -80px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero h1 {
        color: white !important;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero p {
        color: #D8F3EA;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 50px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 16px;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0 18px;
    }

    .section-number {
        background: #DDF3EB;
        color: #127566;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-weight: 800;
    }

    .section-title {
        color: #163B39;
        font-size: 1.3rem;
        font-weight: 750;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
    }

    div[data-testid="stWidgetLabel"] p {
        color: #315A52 !important;
        font-weight: 600;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #F7FAF9;
        color: #163B39;
        border-radius: 10px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(115deg, #127566, #20A38B);
        color: white;
        border: none;
        border-radius: 14px;
        min-height: 55px;
        font-size: 1.05rem;
        font-weight: 750;
        box-shadow: 0 9px 23px rgba(18, 117, 102, 0.22);
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(115deg, #0D6255, #188E79);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 13px 26px rgba(18, 117, 102, 0.28);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF, #EAF7F1);
        padding: 23px;
        border-radius: 18px;
        border: 1px solid #D7E9E0;
        box-shadow: 0 7px 22px rgba(22, 73, 59, 0.07);
    }

    div[data-testid="stMetricValue"] {
        color: #127566;
        font-weight: 800;
    }

    div[data-testid="stMetricLabel"] {
        color: #486A62;
    }

    hr {
        border-color: #D5E7DE !important;
    }

    .footer {
        text-align: center;
        padding: 25px 10px;
        color: #6F9187;
        font-size: 0.85rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem;
        }

        .hero {
            padding: 25px 20px;
            border-radius: 18px;
        }

        .hero h1 {
            font-size: 2.1rem;
        }

        .section-title {
            font-size: 1.1rem;
        }
    }

/* CORREGIR COLOR DE ETIQUETAS */


/* CORRECCION DEFINITIVA DE ETIQUETAS */

/* Etiquetas de todas las casillas numericas */
[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] label *,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {
    color: #173D37 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    -webkit-text-fill-color: #173D37 !important;
}

/* Numeros dentro de las casillas */
[data-testid="stNumberInput"] input {
    color: #173D37 !important;
    -webkit-text-fill-color: #173D37 !important;
    background-color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Textos de ayuda */
[data-testid="stCaptionContainer"] p {
    color: #58776F !important;
    opacity: 1 !important;
}

/* TARJETAS DEL MENU DE PARTIDAS */

.st-key-menu_partidas div.stButton > button {
    min-height: 145px;
    width: 100%;
    border-radius: 20px;
    border: 2px solid #C9E4D9;
    background: #FFFFFF;
    color: #163B39;
    font-size: 1.25rem;
    font-weight: 750;
    box-shadow: 0 8px 22px rgba(18, 92, 78, 0.09);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.st-key-menu_partidas div.stButton > button:hover:not(:disabled) {
    transform: translateY(-3px);
    border-color: #16816E;
    color: #127566;
    background: #F3FBF7;
}

.st-key-menu_partidas div.stButton > button:disabled {
    opacity: 0.65;
    color: #6F9187;
    background: #F4F8F6;
}

/* BOTON VOLVER A ELEGIR PARTIDA */

.st-key-volver_partidas button {
    background-color: #FFFFFF !important;
    color: #163B39 !important;
    border: 1px solid #C9E4D9 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* COLOR DE LAS LETRAS */

.st-key-volver_partidas button p,
.st-key-volver_partidas button span {
    color: #163B39 !important;
    -webkit-text-fill-color: #163B39 !important;
}

/* EFECTO AL PASAR EL CURSOR */

.st-key-volver_partidas button:hover {
    background-color: #EAF7F1 !important;
    color: #127566 !important;
    border-color: #127566 !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. RESULTADOS INICIALES EN CERO
# ==========================================

def resultados_vacios():
    return {
        "superficie": 0.0,
        "superficie_vanos": 0.0,
        "superficie_neta": 0.0,
        "volumen": 0.0,
        "ladrillos": 0,
        "ladrillos_finales": 0,
        "mortero": 0.0,
        "mortero_final": 0.0,
        "superficie_modular": 0.0,
        "detalle_vanos": []
    }


if "resultados" not in st.session_state:
    st.session_state.resultados = resultados_vacios()
# Partida elegida por el usuario
if "partida_seleccionada" not in st.session_state:
    st.session_state.partida_seleccionada = None

# ==========================================
# 4. PORTADA PRINCIPAL
# ==========================================

st.markdown("""
<div class="hero">
    <span class="hero-tag">HERRAMIENTA DE CUBICACIÓN</span>
    <h1>🧱 CubiSmart</h1>
    <p>
        Selecciona una partida de construcción para comenzar
        a cubicar sus materiales de forma sencilla. 
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. FUNCION PARA TITULOS
# ==========================================

# ==========================================
# 6. MENU DE SELECCION DE PARTIDAS
# ==========================================

if st.session_state.partida_seleccionada is None:

    st.markdown("## ¿Qué partida deseas cubicar?")

    st.caption(
        "Selecciona una tarjeta para ingresar las dimensiones."
    )

    with st.container(key="menu_partidas"):

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🧱 Albañilería",
                key="partida_albanileria",
                use_container_width=True
            ):
                st.session_state.partida_seleccionada = "albanileria"
                st.rerun()

        with col2:
            st.button(
                "🏗️ Hormigón · Próximamente",
                key="partida_hormigon",
                use_container_width=True,
                disabled=True
            )

        col3, col4 = st.columns(2)

        with col3:
            st.button(
                "🎨 Pintura · Próximamente",
                key="partida_pintura",
                use_container_width=True,
                disabled=True
            )

        with col4:
            st.button(
                "🚰 Instalaciones · Próximamente",
                key="partida_instalaciones",
                use_container_width=True,
                disabled=True
            )

    # Ocultar los calculos hasta seleccionar una partida
    st.stop()


# BOTON PARA VOLVER AL MENU

if st.button(
    "← Volver a elegir partida",
    key="volver_partidas"
):
    st.session_state.partida_seleccionada = None
    st.session_state.resultados = resultados_vacios()
    st.rerun()

st.markdown("### 🧱 Cubicación de albañilería")

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


# ==========================================
# 6. DIMENSIONES DEL MURO
# ==========================================

titulo_seccion("01", "Dimensiones del muro")

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:
        largo = st.number_input(
            "Largo del muro (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f"
        )

    with col2:
        alto = st.number_input(
            "Alto del muro (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            format="%.2f"
        )

    st.caption(
        "Introduce las dimensiones generales del muro en metros."
    )


# ==========================================
# 7. VANOS DEL MURO
# ==========================================

titulo_seccion("02", "Vanos del muro")

with st.container(border=True):

    cantidad_vanos = st.number_input(
        "Cantidad de vanos",
        min_value=0,
        max_value=30,
        value=0,
        step=1
    )

    st.caption(
        "Considera puertas, ventanas y otras aberturas."
    )

    vanos = []

    for numero in range(cantidad_vanos):

        st.markdown(f"#### Vano {numero + 1}")

        col1, col2 = st.columns(2)

        with col1:
            ancho_vano = st.number_input(
                f"Ancho del vano {numero + 1} (m)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.2f",
                key=f"ancho_vano_{numero}"
            )

        with col2:
            alto_vano = st.number_input(
                f"Alto del vano {numero + 1} (m)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                format="%.2f",
                key=f"alto_vano_{numero}"
            )

        vanos.append((ancho_vano, alto_vano))


# ==========================================
# 8. CARACTERISTICAS DEL LADRILLO
# ==========================================

titulo_seccion("03", "Características del ladrillo")

with st.container(border=True):

    st.info(
        "Ingresa el largo y el alto de la cara visible "
        "del ladrillo. El ancho corresponde al espesor "
        "del muro en este modelo simplificado."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        largo_ladrillo = st.number_input(
            "Largo (m)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.3f"
        )

    with col2:
        alto_ladrillo = st.number_input(
            "Alto (m)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.3f"
        )

    with col3:
        ancho_ladrillo = st.number_input(
            "Ancho (m)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.3f"
        )

    junta_mortero = st.number_input(
        "Espesor de junta de mortero (m)",
        min_value=0.0,
        value=0.0,
        step=0.005,
        format="%.3f"
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
        porcentaje_perdida = st.number_input(
            "Pérdida de ladrillos (%)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.1f"
        )

    with col2:
        porcentaje_perdida_mortero = st.number_input(
            "Pérdida de mortero (%)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.1f"
        )

    st.caption(
        "Introduce los porcentajes de pérdida "
        "que deseas considerar en el cálculo."
    )


# ==========================================
# 10. BOTONES
# ==========================================

st.write("")

col_calcular, col_limpiar = st.columns([3, 1])

with col_calcular:
    calcular = st.button(
        "🧮 Calcular cubicación",
        type="primary",
        use_container_width=True
    )

with col_limpiar:
    limpiar = st.button(
        "Limpiar resultados",
        use_container_width=True
    )


# ==========================================
# 11. LIMPIAR RESULTADOS
# ==========================================

if limpiar:
    st.session_state.resultados = resultados_vacios()


# ==========================================
# 12. OPERACIONES MATEMATICAS
# ==========================================

if calcular:

    # VALIDAR MURO

    if largo <= 0 or alto <= 0:
        st.error(
            "El largo y el alto del muro deben ser mayores que cero."
        )
        st.stop()

    # VALIDAR LADRILLO

    if (
        largo_ladrillo <= 0
        or alto_ladrillo <= 0
        or ancho_ladrillo <= 0
    ):
        st.error(
            "Todas las dimensiones del ladrillo deben ser mayores que cero."
        )
        st.stop()

    # VALIDAR LOS VANOS

    superficie_total_vanos = 0.0
    superficies_individuales = []

    for numero, (ancho_vano, alto_vano) in enumerate(vanos):

        if ancho_vano <= 0 or alto_vano <= 0:
            st.error(
                f"Las dimensiones del vano {numero + 1} "
                "deben ser mayores que cero."
            )
            st.stop()

        if ancho_vano > largo or alto_vano > alto:
            st.error(
                f"El vano {numero + 1} supera las "
                "dimensiones del muro."
            )
            st.stop()

        superficie_vano = ancho_vano * alto_vano

        superficie_total_vanos += superficie_vano

        superficies_individuales.append(superficie_vano)

    # CALCULAR SUPERFICIE DEL MURO

    superficie = largo * alto

    superficie_neta = superficie - superficie_total_vanos

    if superficie_neta <= 0:
        st.error(
            "La superficie total de vanos es igual o "
            "superior a la superficie del muro."
        )
        st.stop()

    # CALCULAR VOLUMEN DEL MURO

    espesor = ancho_ladrillo

    volumen = superficie_neta * espesor

    # DIMENSIONES MODULARES

    largo_modular = largo_ladrillo + junta_mortero
    alto_modular = alto_ladrillo + junta_mortero

    superficie_modular = largo_modular * alto_modular
    superficie_ladrillo = largo_ladrillo * alto_ladrillo

    # CALCULAR LADRILLOS

    cantidad_ladrillos = superficie_neta / superficie_modular

    ladrillos_redondeados = math.ceil(
        round(cantidad_ladrillos, 9)
    )

    cantidad_con_perdida = cantidad_ladrillos * (
        1 + porcentaje_perdida / 100
    )

    ladrillos_finales = math.ceil(
        round(cantidad_con_perdida, 9)
    )

    # CALCULAR MORTERO

    volumen_ladrillo = (
        largo_ladrillo
        * alto_ladrillo
        * ancho_ladrillo
    )

    volumen_modular = (
        largo_modular
        * alto_modular
        * ancho_ladrillo
    )

    mortero_por_modulo = volumen_modular - volumen_ladrillo

    mortero_total = mortero_por_modulo * cantidad_ladrillos

    mortero_final = mortero_total * (
        1 + porcentaje_perdida_mortero / 100
    )

    # GUARDAR RESULTADOS EN LA SESION

    st.session_state.resultados = {
        "superficie": superficie,
        "superficie_vanos": superficie_total_vanos,
        "superficie_neta": superficie_neta,
        "volumen": volumen,
        "ladrillos": ladrillos_redondeados,
        "ladrillos_finales": ladrillos_finales,
        "mortero": mortero_total,
        "mortero_final": mortero_final,
        "superficie_modular": superficie_modular,
        "detalle_vanos": superficies_individuales
    }

    st.success("¡Cubicación calculada correctamente!")


# ==========================================
# 13. RESULTADOS SIEMPRE VISIBLES
# ==========================================

r = st.session_state.resultados

st.divider()

st.markdown("## 📊 Resultados de cubicación")

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

st.warning(
    "Los resultados son estimaciones geométricas "
    "para un prototipo académico. No consideran "
    "todas las características constructivas, "
    "mortero dentro de perforaciones ni "
    "superposición entre vanos. "
    "Verifica las especificaciones y rendimientos "
    "antes de utilizarlos en una obra real."
)


# ==========================================
# 14. PIE DE PAGINA
# ==========================================

st.markdown("""
<div class="footer">
    CubiSmart · Prototipo de cubicación de albañilería<br>
    Desarrollado con Python y Streamlit
</div>
""", unsafe_allow_html=True)
