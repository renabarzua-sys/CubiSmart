"""CubiSmart: partidas.calculos_albanileria."""
import math

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


def calcular_muro(datos):
    largo = datos['dato_largo_muro']
    alto = datos['dato_alto_muro']
    largo_ladrillo = datos['dato_largo_ladrillo']
    alto_ladrillo = datos['dato_alto_ladrillo']
    ancho_ladrillo = datos['dato_ancho_ladrillo']
    junta_mortero = datos['dato_junta_mortero']
    porcentaje_perdida = datos['dato_perdida_ladrillos']
    porcentaje_perdida_mortero = datos['dato_perdida_mortero']
    vanos = [(datos.get(f'dato_ancho_vano_{i}', 0.0), datos.get(f'dato_alto_vano_{i}', 0.0)) for i in range(datos['dato_cantidad_vanos'])]
    if not all(math.isfinite(v) and v >= 0 for v in [largo, alto, largo_ladrillo, alto_ladrillo, ancho_ladrillo, junta_mortero, porcentaje_perdida, porcentaje_perdida_mortero, *(v for par in vanos for v in par)]):
        raise ValueError('Los datos deben ser números finitos y no negativos.')


    # VALIDAR MURO

    if largo <= 0 or alto <= 0:
        raise ValueError(
            "El largo y el alto del muro deben ser mayores que cero."
        )

    # VALIDAR LADRILLO

    if (
        largo_ladrillo <= 0
        or alto_ladrillo <= 0
        or ancho_ladrillo <= 0
    ):
        raise ValueError(
            "Todas las dimensiones del ladrillo deben ser mayores que cero."
        )

    # VALIDAR LOS VANOS

    superficie_total_vanos = 0.0
    superficies_individuales = []

    for numero, (ancho_vano, alto_vano) in enumerate(vanos):

        if ancho_vano <= 0 or alto_vano <= 0:
            raise ValueError(
                f"Las dimensiones del vano {numero + 1} "
                "deben ser mayores que cero."
            )

        if ancho_vano > largo or alto_vano > alto:
            raise ValueError(
                f"El vano {numero + 1} supera las "
                "dimensiones del muro."
            )

        superficie_vano = ancho_vano * alto_vano

        superficie_total_vanos += superficie_vano

        superficies_individuales.append(superficie_vano)

    # CALCULAR SUPERFICIE DEL MURO

    superficie = largo * alto

    superficie_neta = superficie - superficie_total_vanos

    if superficie_neta <= 0:
        raise ValueError(
            "La superficie total de vanos es igual o "
            "superior a la superficie del muro."
        )

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

    return {
        "superficie": superficie,
        "superficie_vanos": superficie_total_vanos,
        "superficie_neta": superficie_neta,
        "volumen": volumen,
        "ladrillos": ladrillos_redondeados,
        "ladrillos_finales": ladrillos_finales,
        "mortero": mortero_total,
        "mortero_final": mortero_final,
        "superficie_modular": superficie_modular,
        "detalle_vanos": superficies_individuales,
        "memoria": {
            "largo": largo,
            "alto": alto,
            "espesor": espesor,
            "largo_ladrillo": largo_ladrillo,
            "alto_ladrillo": alto_ladrillo,
            "ancho_ladrillo": ancho_ladrillo,
            "junta_mortero": junta_mortero,
            "largo_modular": largo_modular,
            "alto_modular": alto_modular,
            "cantidad_ladrillos": cantidad_ladrillos,
            "cantidad_con_perdida": cantidad_con_perdida,
            "porcentaje_perdida": porcentaje_perdida,
            "porcentaje_perdida_mortero": porcentaje_perdida_mortero,
            "volumen_ladrillo": volumen_ladrillo,
            "volumen_modular": volumen_modular,
            "mortero_por_modulo": mortero_por_modulo,
            "vanos": vanos.copy()
        }
    }


