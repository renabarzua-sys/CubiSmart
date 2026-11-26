
import math

print("================================")
print("           CUBISMART")
print("    Cubicacion de Materiales")
print("================================")

# INGRESAR DIMENSIONES DEL MURO

largo = float(input("Ingrese el largo del muro en metros: "))
alto = float(input("Ingrese el alto del muro en metros: "))

# VALIDAR DIMENSIONES DEL MURO

if largo <= 0:
    print("Error: el largo debe ser mayor que cero.")
    raise SystemExit

if alto <= 0:
    print("Error: el alto debe ser mayor que cero.")
    raise SystemExit

superficie = largo * alto

# INGRESAR Y VALIDAR LOS VANOS

cantidad_vanos = int(input("¿Cuantos vanos tiene el muro?: ")) 

if cantidad_vanos < 0:
    print("Error: la cantidad de vanos no puede ser negativa.")
    raise SystemExit

superficie_total_vanos = 0

for numero in range(cantidad_vanos):

    print(f"\n-------- VANO {numero + 1} --------")

    ancho_vano = float(input("Ingrese el ancho del vano en metros: "))
    alto_vano = float(input("Ingrese el alto del vano en metros: "))

    if ancho_vano <= 0:
        print("Error: el ancho del vano debe ser mayor que cero.")
        raise SystemExit

    if alto_vano <= 0:
        print("Error: el alto del vano debe ser mayor que cero.")
        raise SystemExit

    if ancho_vano > largo:
        print("Error: el vano no puede ser mas ancho que el muro.")
        raise SystemExit

    if alto_vano > alto:
        print("Error: el vano no puede ser mas alto que el muro.")
        raise SystemExit

    superficie_vano = ancho_vano * alto_vano

    superficie_total_vanos = superficie_total_vanos + superficie_vano

    print(f"Superficie del vano {numero + 1}: {superficie_vano:.2f} m²")

# CALCULAR SUPERFICIE NETA

superficie_neta = superficie - superficie_total_vanos

if superficie_neta <= 0:
    print("Error: la superficie total de vanos es igual o superior a la del muro.")
    raise SystemExit

# CALCULAR VOLUMEN DEL MURO

espesor = float(input("\nIngrese el espesor del muro en metros: "))

if espesor <= 0:
    print("Error: el espesor debe ser mayor que cero.")
    raise SystemExit

volumen = superficie_neta * espesor

# INGRESAR DIMENSIONES DEL LADRILLO

largo_ladrillo = float(input("Ingrese el largo del ladrillo en metros: "))
alto_ladrillo = float(input("Ingrese el alto del ladrillo en metros: "))
ancho_ladrillo = float(input("Ingrese el ancho del ladrillo en metros: "))

# VALIDAR DIMENSIONES DEL LADRILLO

if largo_ladrillo <= 0 or alto_ladrillo <= 0 or ancho_ladrillo <= 0:
    print("Error: las dimensiones del ladrillo deben ser mayores que cero.")
    raise SystemExit

if not math.isclose(espesor, ancho_ladrillo, abs_tol=0.000001):
    print("Error: el espesor del muro debe coincidir con el ancho del ladrillo en este modelo.")
    raise SystemExit

# INGRESAR JUNTA DE MORTERO

junta_mortero = float(input("Ingrese el espesor de la junta de mortero en metros: "))

if junta_mortero < 0:
    print("Error: la junta de mortero no puede ser negativa.")
    raise SystemExit

# CALCULAR SUPERFICIES Y VOLUMENES DEL LADRILLO

largo_modular = largo_ladrillo + junta_mortero
alto_modular = alto_ladrillo + junta_mortero

superficie_modular = largo_modular * alto_modular
superficie_ladrillo = largo_ladrillo * alto_ladrillo

volumen_ladrillo = largo_ladrillo * alto_ladrillo * ancho_ladrillo

# CALCULAR VOLUMEN DEL MODULO DE ALBAÑILERIA

volumen_modular = largo_modular * alto_modular * ancho_ladrillo

# CALCULAR MORTERO POR MODULO

mortero_por_modulo = volumen_modular - volumen_ladrillo

# CALCULAR CANTIDAD DE LADRILLOS

cantidad_ladrillos = superficie_neta / superficie_modular

ladrillos_redondeados = math.ceil(round(cantidad_ladrillos, 9))

# CALCULAR MORTERO TOTAL

mortero_total = mortero_por_modulo * cantidad_ladrillos
porcentaje_perdida_mortero = float(input("ingrese porcentaje de perdida del mortero: "))
mortero_final = mortero_total * (1 + porcentaje_perdida_mortero / 100)

# INGRESAR PORCENTAJE DE PERDIDA DE LADRILLOS

porcentaje_perdida = float(input("Ingrese el porcentaje de perdida de ladrillos: "))

if porcentaje_perdida < 0:
    print("Error: el porcentaje de pérdida no puede ser negativo.")
    raise SystemExit

cantidad_con_perdida = cantidad_ladrillos * (1 + porcentaje_perdida / 100)

ladrillos_finales = math.ceil(round(cantidad_con_perdida, 9))

# MOSTRAR RESULTADOS

print("\n======== RESULTADOS CUBISMART ========")

print(f"Superficie total del muro: {superficie:.2f} m²")
print(f"Cantidad de vanos: {cantidad_vanos}")
print(f"Superficie total de vanos: {superficie_total_vanos:.2f} m²")
print(f"Superficie neta del muro: {superficie_neta:.2f} m²")
print(f"Volumen neto del muro: {volumen:.2f} m³")

print("\n-------- LADRILLOS --------")

print(f"Superficie del ladrillo: {superficie_ladrillo:.4f} m²")
print(f"Superficie modular del ladrillo: {superficie_modular:.4f} m²")
print(f"Cantidad estimada de ladrillos: {ladrillos_redondeados} unidades")
print(f"Cantidad de ladrillos con {porcentaje_perdida:.1f}% de pérdida: {ladrillos_finales} unidades")

print("\n-------- MORTERO DE PEGA --------")

print(f"Volumen de un ladrillo: {volumen_ladrillo:.6f} m³")
print(f"Volumen de un modulo: {volumen_modular:.6f} m³")
print(f"Mortero por modulo: {mortero_por_modulo:.6f} m³")
print(f"Mortero total estimado: {mortero_total:.4f} m³")
print(f"Mortero con {porcentaje_perdida_mortero:.1f}% de pérdida: {mortero_final:.4f} m³")

print("\n=====================================")
