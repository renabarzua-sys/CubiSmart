"""CubiSmart: servicios.estado."""
from partidas.calculos_albanileria import resultados_vacios
import streamlit as st

S = st.session_state
BASE = {k: 0.0 for k in ['dato_largo_muro','dato_alto_muro','dato_largo_ladrillo','dato_alto_ladrillo','dato_ancho_ladrillo','dato_junta_mortero','dato_perdida_ladrillos','dato_perdida_mortero']}
BASE['dato_cantidad_vanos'] = 0
for i in range(30):
    BASE[f'dato_ancho_vano_{i}'] = 0.0
    BASE[f'dato_alto_vano_{i}'] = 0.0
PRUEBA = dict(BASE, dato_largo_muro=6.0, dato_alto_muro=2.5, dato_cantidad_vanos=2, dato_ancho_vano_0=.9, dato_alto_vano_0=2., dato_ancho_vano_1=1.2, dato_alto_vano_1=1., dato_largo_ladrillo=.29, dato_alto_ladrillo=.14, dato_ancho_ladrillo=.14, dato_junta_mortero=.01, dato_perdida_ladrillos=5., dato_perdida_mortero=10.)

def inicializar_estado():
    for k,v in BASE.items():
        S[k] = S.get(k,v)
    for k,v in {'resultados':resultados_vacios(), 'muros_guardados':{}, 'muro_en_edicion':None, 'dato_nombre_muro':'Muro 01', 'partida_seleccionada':None, 'vista_actual':'🧮 Cubicación'}.items():
        S[k] = S.get(k,v)
    # Mantener también parámetros de dosificación al navegar
    for k in list(S.keys()):
        if k.startswith('dos_'):
            S[k] = S[k]
