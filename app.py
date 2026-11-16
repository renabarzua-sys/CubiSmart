
import math
import streamlit as st

# ==========================================
# 1. CONFIGURACION GENERAL
# ==========================================

st.set_page_config(
    page_title="CubiSmart | Cubicación de materiales",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. DISEÑO VISUAL
# ==========================================

st.markdown("""
<style>

/* FONDO GENERAL */
.stApp {
    background:
        radial-gradient(circle at 85% 5%, #D5EEE5 0%, transparent 35%),
        radial-gradient(circle at 5% 80%, #E2EFEC 0%, transparent 35%),
        linear-gradient(135deg, #F5F9F7, #E9F3EF);
}

.block-container {
    max-width: 1100px;
    padding: 2rem 3rem 4rem;
}

/* TITULOS */
h1, h2, h3, h4 {
    color: #163B39 !important;
    letter-spacing: -0.5px;
}

/* PORTADA */
.hero {
    background: linear-gradient(115deg, #124F49, #208C79);
    padding: 35px 38px;
    border-radius: 24px;
    margin-bottom: 25px;
    box-shadow: 0 15px 35px rgba(15,87,73,0.20);
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
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
    pointer-events: none;
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero p {
    color: #E0F7EE !important;
    font-size: 1.05rem;
}

.hero-tag {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.20);
    border-radius: 50px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 16px;
}

/* TITULOS DE SECCIONES */
.section-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 18px 0;
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

/* CUADROS DE FORMULARIO */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px;
}

/* ETIQUETAS SOBRE LAS MEDIDAS */
[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] label *,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {
    color: #173D37 !important;
    -webkit-text-fill-color: #173D37 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

/* CASILLAS NUMERICAS */
[data-testid="stNumberInput"] input {
    color: #173D37 !important;
    -webkit-text-fill-color: #173D37 !important;
    background-color: #FFFFFF !important;
    border-radius: 10px;
    font-weight: 600;
}

/* BOTONES DE MENOS Y MAS */
[data-testid="stNumberInput"] button {
    background-color: #DDF3EB !important;
    color: #173D37 !important;
    border-color: #B8DDD0 !important;
}

[data-testid="stNumberInput"] button svg {
    color: #173D37 !important;
    stroke: #173D37 !important;
}

[data-testid="stNumberInput"] button:hover {
    background-color: #BDE5D7 !important;
}

/* TEXTOS DEBAJO DE LAS CASILLAS */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {
    color: #173D37 !important;
    -webkit-text-fill-color: #173D37 !important;
    opacity: 1 !important;
    font-weight: 500 !important;
}

/* TEXTO GENERAL */
[data-testid="stMarkdownContainer"] p {
    line-height: 1.6;
}

/* BOTON PRINCIPAL */
.stButton > button[kind="primary"] {
    background: linear-gradient(115deg, #127566, #20A38B);
    color: #FFFFFF !important;
    border: none;
    border-radius: 14px;
    min-height: 55px;
    font-size: 1.05rem;
    font-weight: 750;
    box-shadow: 0 9px 23px rgba(18,117,102,0.22);
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(115deg, #0D6255, #188E79);
    transform: translateY(-2px);
}

/* BOTON LIMPIAR */
.stButton > button[kind="secondary"] {
    background-color: #E2F1EB;
    color: #173D37 !important;
    border: 1px solid #B8DDD0;
    border-radius: 14px;
    min-height: 55px;
}

/* TARJETAS DE RESULTADOS */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF, #EAF7F1);
    padding: 23px;
    border: 1px solid #D7E9E0;
    border-radius: 18px;
    box-shadow: 0 7px 22px rgba(22,73,59,0.07);
}

/* NOMBRES DE LOS RESULTADOS */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #173D37 !important;
    -webkit-text-fill-color: #173D37 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

/* NUMEROS DE LOS RESULTADOS */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #127566 !important;
    -webkit-text-fill-color: #127566 !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}

/* SEPARADORES */
hr {
    border-color: #D5E7DE !important;
}

/* PIE DE PAGINA */
.footer {
    text-align: center;
    padding: 25px 10px;
    color: #406A60;
    font-size: 0.85rem;
}

/* ADAPTACION PARA CELULARES */
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

    [data-testid="stMetric"] {
        padding: 15px;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. RESULTADOS INICIALES VACIOS
# ==========================================

if "resultados" not in st.session_state:
    st.session_state.resultados = None


# ==========================================
# 4. PORTADA
# ==========================================

st.markdown("""
<div class="hero">
    <span class="hero-tag">HERRAMIENTA DE CUBICACIÓN</span>
    <h1>🧱 CubiSmart</h1>
    <p>
        Calcula las cantidades estimadas de ladrillos
        y mortero para tus proyectos de albañilería.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. FUNCION PARA TITULOS
# ==========================================

def titulo_seccion(numero, nombre):
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="section-number">{numero}</div>
            <div class="section-title">{nombre}</div>
        </div>
        """,
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
            value=None,
            step=0.1,
            format="%.2f",
            key="largo_muro"
        )

    with col2:
        alto = st.number_input(
            "Alto del muro (m)",
            min_value=0.0,
            value=None,
            step=0.1,
            format="%.2f",
            key="alto_muro"
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
        value=None,
        step=1,
        key="cantidad_vanos"
    )

    st.caption(
        "Si el muro no tiene vanos, deja la casilla vacía "
        "o escribe 0."
    )

    vanos = []

    for numero in range(cantidad_vanos or 0):

        st.markdown(f"#### Vano {numero + 1}")

        col1, col2 = st.columns(2)

        with col1:
            ancho_vano = st.number_input(
                f"Ancho del vano {numero + 1} (m)",
                min_value=0.0,
                value=None,
                step=0.1,
                format="%.2f",
                key=f"ancho_vano_{numero}"
            )

        with col2:
            alto_vano = st.number_input(
                f"Alto del vano {numero + 1} (m)",
                min_value=0.0,
                value=None,
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
        "Ingresa el largo y alto de la cara visible "
        "del ladrillo. El ancho representa el espesor "
        "del muro en este modelo."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        largo_ladrillo = st.number_input(
            "Largo (m)",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.3f",
            key="largo_ladrillo"
        )

    with col2:
        alto_ladrillo = st.number_input(
            "Alto (m)",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.3f",
            key="alto_ladrillo"
        )

    with col3:
        ancho_ladrillo = st.number_input(
            "Ancho (m)",
            min_value=0.0,
            value=None,
            step=0.01,
            format="%.3f",
            key="ancho_ladrillo"
        )

    junta_mortero = st.number_input(
        "Espesor de junta de mortero (m)",
        min_value=0.0,
        value=None,
        step=0.005,
        format="%.3f",
        key="junta_mortero"
    )

    st.caption(
        "Ejemplo: 1 cm de junta equivale a 0.010 m."
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
            value=None,
            step=1.0,
            format="%.1f",
            key="perdida_ladrillos"
        )

    with col2:
        porcentaje_perdida_mortero = st.number_input(
            "Pérdida de mortero (%)",
            min_value=0.0,
            value=None,
            step=1.0,
            format="%.1f",
            key="perdida_mortero"
        )

    st.caption(
        "Si no deseas considerar pérdidas, escribe 0 "
        "en ambos campos."
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
    st.session_state.resultados = None


# ==========================================
# 12. CALCULOS
# ==========================================

if calcular:

    # VALIDAR CAMPOS OBLIGATORIOS

    campos = {
        "Largo del muro": largo,
        "Alto del muro": alto,
        "Largo del ladrillo": largo_ladrillo,
        "Alto del ladrillo": alto_ladrillo,
        "Ancho del ladrillo": ancho_ladrillo,
        "Espesor de junta": junta_mortero,
        "Pérdida de ladrillos": porcentaje_perdida,
        "Pérdida de mortero": porcentaje_perdida_mortero
    }

    for nombre, valor in campos.items():
        if valor is None:
            st.error(f"Debes ingresar: {nombre}.")
            st.stop()

    if largo <= 0 or alto <= 0:
        st.error(
            "Las dimensiones del muro deben ser mayores que cero."
        )
        st.stop()

    if (
        largo_ladrillo <= 0
        or alto_ladrillo <= 0
        or ancho_ladrillo <= 0
    ):
        st.error(
            "Las dimensiones del ladrillo deben ser mayores que cero."
        )
        st.stop()

    # CALCULAR VANOS

    superficie_total_vanos = 0.0
    superficies_individuales = []

    for numero, (ancho_vano, alto_vano) in enumerate(vanos):

        if ancho_vano is None or alto_vano is None:
            st.error(
                f"Debes completar las medidas del vano {numero + 1}."
            )
            st.stop()

        if ancho_vano <= 0 or alto_vano <= 0:
            st.error(
                f"Las medidas del vano {numero + 1} "
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

    # SUPERFICIE DEL MURO

    superficie = largo * alto
    superficie_neta = superficie - superficie_total_vanos

    if superficie_neta <= 0:
        st.error(
            "La superficie de los vanos es igual o superior "
            "a la superficie del muro."
        )
        st.stop()

    # VOLUMEN DEL MURO

    espesor = ancho_ladrillo
    volumen = superficie_neta * espesor

    # SUPERFICIE MODULAR DEL LADRILLO

    largo_modular = largo_ladrillo + junta_mortero
    alto_modular = alto_ladrillo + junta_mortero

    superficie_modular = largo_modular * alto_modular

    # CANTIDAD DE LADRILLOS

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

    # MORTERO DE PEGA

    volumen_ladrillo = (
        largo_ladrillo * alto_ladrillo * ancho_ladrillo
    )

    volumen_modular = (
        largo_modular * alto_modular * ancho_ladrillo
    )

    mortero_por_modulo = volumen_modular - volumen_ladrillo

    mortero_total = mortero_por_modulo * cantidad_ladrillos

    mortero_final = mortero_total * (
        1 + porcentaje_perdida_mortero / 100
    )

    # GUARDAR RESULTADOS

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


# FUNCION PARA MOSTRAR RESULTADOS

def mostrar_resultado(nombre, clave, decimales=2, unidad=""):

    if r is None:
        valor = "—"

    elif decimales == 0:
        valor = f"{r[clave]:.0f} {unidad}".strip()

    else:
        valor = f"{r[clave]:.{decimales}f} {unidad}".strip()

    st.metric(nombre, valor)


# RESULTADOS DEL MURO

st.markdown("### 📐 Superficies del muro")

col1, col2 = st.columns(2)

with col1:
    mostrar_resultado("Superficie total", "superficie", 2, "m²")
    mostrar_resultado(
        "Superficie de vanos", "superficie_vanos", 2, "m²"
    )

with col2:
    mostrar_resultado(
        "Superficie neta", "superficie_neta", 2, "m²"
    )
    mostrar_resultado("Volumen del muro", "volumen", 3, "m³")


# DETALLE DE VANOS

if r is not None and r["detalle_vanos"]:

    with st.expander("Ver detalle de vanos"):
        for numero, area in enumerate(r["detalle_vanos"]):
            st.write(f"Vano {numero + 1}: {area:.2f} m²")


# RESULTADOS DE LADRILLOS

st.divider()
st.markdown("### 🧱 Cantidad de ladrillos")

col1, col2 = st.columns(2)

with col1:
    mostrar_resultado("Cantidad teórica", "ladrillos", 0, "unidades")

with col2:
    mostrar_resultado(
        "Cantidad con pérdidas", "ladrillos_finales", 0, "unidades"
    )

if r is not None:
    st.caption(
        f"Superficie modular del ladrillo: "
        f"{r['superficie_modular']:.4f} m²"
    )


# RESULTADOS DE MORTERO

st.divider()
st.markdown("### 🪣 Mortero de pega")

col1, col2 = st.columns(2)

with col1:
    mostrar_resultado("Mortero teórico", "mortero", 4, "m³")

with col2:
    mostrar_resultado(
        "Mortero con pérdidas", "mortero_final", 4, "m³"
    )

if r is not None:
    st.caption(
        f"Volumen equivalente con pérdidas: "
        f"{r['mortero_final'] * 1000:.2f} litros"
    )
else:
    st.caption(
        "Ingresa las medidas y presiona Calcular cubicación "
        "para visualizar los resultados."
    )

st.warning(
    "Estimación geométrica para prototipo académico. "
    "No considera perforaciones del ladrillo, "
    "juntas parciales ni superposición entre vanos. "
    "Verifica los rendimientos antes de utilizar "
    "las cantidades en una obra real."
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
