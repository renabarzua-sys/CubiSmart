"""Campos numéricos comunes: un guion indica un campo vacío, equivalente a cero."""
import streamlit as st


def numero(contenedor, etiqueta, **opciones):
    minimo = opciones.get('min_value')
    if minimo != 0:
        return contenedor.number_input(etiqueta, **opciones)
    clave = opciones.get('key')
    if clave is not None and clave in st.session_state:
        if st.session_state[clave] == 0:
            st.session_state[clave] = None
        # El estado de sesión conserva los valores cargados de los muros.
        opciones['value'] = None
    elif opciones.get('value', 0) == 0:
        opciones['value'] = None
    opciones.setdefault('placeholder', '—')
    valor = contenedor.number_input(etiqueta, **opciones)
    return (0 if isinstance(minimo, int) else 0.0) if valor is None else valor
