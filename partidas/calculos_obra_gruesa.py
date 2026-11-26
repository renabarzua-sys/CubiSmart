"""Cubicación geométrica; no dimensionamiento estructural ni dosificación certificada."""
from math import isfinite, pi
from partidas.catalogo import CATEGORIAS
CAT = {c:(n,u) for c,n,u in CATEGORIAS['Obra gruesa'] if c!='2.9'}
# campo, etiqueta, valor inicial, mínimo estricto (excepto descuentos y pérdidas)
L=('largo','Largo / longitud (m)',0.,True); A=('ancho','Ancho (m)',0.,True); H=('alto','Altura / profundidad (m)',0.,True)
E=('espesor','Espesor (m)',0.,True); D=('descuento','Descuento total (m³)',0.,False); S=('descuento','Descuento total (m²)',0.,False)
P=('perdida','Recargo de material (%)',0.,False)
VOLUMEN=(L,A,H,D,P); SUPERFICIE=(L,H,S,P)
HORMIGON = frozenset(('2.2','2.3','2.8','2.11','2.12','2.14'))
GRADOS = ('G-5','G-10','G-15','G-20','G-25','G-30','G-35','G-40','G-45','G-50','Otro')
SIN_GRADO = 'Sin especificar'

def grado_normalizado(valor):
    v = str(valor or '').strip()
    return SIN_GRADO if not v or v.casefold() == SIN_GRADO.casefold() else v.upper()

CAMPOS={
 '2.1':(L,('ancho','Ancho inferior (m)',0.,True),('ancho_sup','Ancho superior (m)',0.,True),H,D,('esponjamiento','Esponjamiento para transporte (%)',0.,False)),
 '2.2':(L,A,E,D,P),'2.3':VOLUMEN,'2.8':VOLUMEN,'2.11':VOLUMEN,'2.12':VOLUMEN,
 '2.4':(('diametro','Diámetro de barra (mm)',0.,True),('longitud','Longitud desarrollada por pieza (m), incluye ganchos y traslapos',0.,True),P),
 '2.5':(('diametro','Diámetro de barra (mm)',0.,True),('longitud','Longitud desarrollada por pieza (m), incluye ganchos y traslapos',0.,True)),
 '2.6':(L,H,('caras','Número de caras iguales por elemento',2.,True),S,P),
 '2.7':(L,H,('caras','Número de caras iguales por elemento',2.,True),S),
 '2.10':(L,H,('caras','Número de caras iguales por elemento',1.,True),S,P),
 '2.13':(L,A,('grava','Espesor compactado de grava (m)',0.,False),('arena','Espesor compactado de arena (m)',0.,False),('factor_grava','Factor volumen suelto / compactado grava',1.,True),('factor_arena','Factor volumen suelto / compactado arena',1.,True)),
 '2.14':(L,A,('espesor','Espesor de hormigón (m)',.07,True),S,P),
 '2.15':(L,H,S,('montantes','Montantes totales por elemento, según plano',0.,False),('soleras','Longitud total de soleras por elemento (m)',0.,False),('refuerzos','Longitud adicional de madera por elemento (m)',0.,False),P),
}
GUIA={
 '2.1':('Excavar zanjas hasta cotas de fundación. Sección trapezoidal constante; para paredes verticales ingresa anchos iguales.','N × L × (ancho inferior + ancho superior) / 2 × profundidad − descuento','tierra excavada, retiro, excavadora, mano de obra'),
 '2.2':('Capa de hormigón pobre que regulariza la base de fundación.','N × L × ancho × espesor − descuento','hormigón del grado especificado, mano de obra, herramientas'),
 '2.3':('Hormigón de fundaciones; usa dimensiones del plano estructural.','N × L × ancho × alto − descuento','hormigón del grado especificado, vibrador, mano de obra'),
 '2.4':('Corte y doblado de barras. Registra cada diámetro y forma por separado, con longitud desarrollada real.','N × longitud × π × (diámetro / 1000)² / 4 × 7850','acero, alambre, cortadora, dobladora, mano de obra'),
 '2.5':('Colocación de acero confeccionado. Evita volver a presupuestar el acero si ya está en confección.','N × longitud × π × (diámetro / 1000)² / 4 × 7850','mano de obra, separadores, alambre si no se incluyó antes'),
 '2.6':('Fabricación de moldajes de sobrecimientos; mide caras de contacto. No equivale automáticamente a compra de tableros (reutilización y cortes).','N × L × altura × caras − descuento','tableros, madera, clavos, mano de obra'),
 '2.7':('Montaje de moldajes confeccionados. No repetir materiales ya presupuestados.','N × L × altura × caras − descuento','mano de obra, fijaciones, desmoldante'),
 '2.8':('Hormigón de sobrecimientos sobre fundaciones.','N × L × ancho × alto − descuento','hormigón del grado especificado, vibrador, mano de obra'),
 '2.10':('Moldajes de pilares y cadenas. Registra por separado caras de distinta medida; no contar caras que no requieren moldaje.','N × L × altura × caras − descuento','tableros, puntales, fijaciones, desmoldante, mano de obra'),
 '2.11':('Hormigón de pilares rectangulares: largo y ancho son lados de sección, alto es altura efectiva. Evita solapes con cadenas.','N × L × ancho × alto − descuento','hormigón del grado especificado, vibrador, mano de obra'),
 '2.12':('Hormigón de cadenas: longitud efectiva sin duplicar intersecciones con pilares u otras cadenas.','N × L × ancho × alto − descuento','hormigón del grado especificado, vibrador, mano de obra'),
 '2.13':('Capas compactadas de grava y arena bajo radier. Factores de suministro definidos por obra; 1 significa sin ajuste.','N × L × ancho × (espesor grava + espesor arena)','grava, arena, placa compactadora, mano de obra'),
 '2.14':('Radier medido en m²; volumen de hormigón se calcula aparte. Espesor inicial 7 cm según catálogo, confirmar planos.','N × L × ancho − descuento; volumen = superficie neta × espesor','hormigón del grado especificado, terminación, mano de obra, equipo'),
 '2.15':('Estructura de madera de tabiques; superficie neta según alcance. Ingresa montantes, soleras y refuerzos reales de plano (incluye vanos y dinteles).','N × L × altura − descuento; madera = N × (montantes × altura + soleras + refuerzos)','madera estructural, fijaciones, mano de obra'),
}

def calcular(codigo,nombre,cantidad,valores,grado=None):
    if codigo not in CAT or not nombre.strip() or not isfinite(cantidad) or cantidad<1 or int(cantidad)!=cantidad: raise ValueError('Nombre o cantidad inválidos.')
    v={k:float(valores[k]) for k,_,_,_ in CAMPOS[codigo]}
    for k,et,_,positivo in CAMPOS[codigo]:
        if not isfinite(v[k]) or v[k]<0 or (positivo and v[k]==0): raise ValueError('Revisa: '+et)
    for k in ('caras','montantes'):
        if k in v and int(v[k])!=v[k]: raise ValueError('Las caras y montantes deben ser enteros.')
    n=int(cantidad); l=v.get('largo',0); a=v.get('ancho',0); h=v.get('alto',0); d=v.get('descuento',0); f=1+v.get('perdida',0)/100; aux={}
    if codigo=='2.1':
        bruto=n*l*(a+v['ancho_sup'])/2*h; aux['Volumen suelto (m³)']=(bruto-d)*(1+v['esponjamiento']/100)
    elif codigo in ('2.4','2.5'):
        kgm=pi*(v['diametro']/1000)**2/4*7850; bruto=n*v['longitud']*kgm; aux={'Longitud total (m)':n*v['longitud'],'Peso teórico (kg/m)':kgm}
        if codigo=='2.4': aux['Acero estimado con pérdida (kg)']=bruto*f
    elif codigo in ('2.6','2.7','2.10'):
        bruto=n*l*h*v['caras']
        if codigo!='2.7': aux['Área equivalente con pérdida (m²)']=(bruto-d)*f
    elif codigo=='2.13':
        g=n*l*a*v['grava']; s=n*l*a*v['arena']; bruto=g+s; aux={'Grava compactada (m³)':g,'Arena compactada (m³)':s,'Grava suministro (m³)':g*v['factor_grava'],'Arena suministro (m³)':s*v['factor_arena']}
    elif codigo=='2.14':
        bruto=n*l*a; aux={'Hormigón neto (m³)':(bruto-d)*v['espesor'],'Hormigón con pérdida (m³)':(bruto-d)*v['espesor']*f}
    elif codigo=='2.15':
        bruto=n*l*h; madera=n*(v['montantes']*h+v['soleras']+v['refuerzos']); aux={'Madera lineal (m)':madera,'Madera con pérdida (m)':madera*f}
    else:
        bruto=n*l*a*v.get('espesor',h); aux['Hormigón con pérdida (m³)']=(bruto-d)*f
    neto=bruto-d
    if neto<=0 or not all(isfinite(x) and x>=0 for x in [bruto,neto,*aux.values()]): raise ValueError('La cantidad neta debe ser positiva y finita; revisa los descuentos.')
    res = {'nombre':nombre.strip(),'cantidad':n,'valores':v,'bruto':bruto,'neto':neto,'aux':aux}
    if codigo in HORMIGON:
        res['grado'] = grado_normalizado(grado)
    return res


def resumen_grados(codigo, registros):
    grupos = {}
    if codigo not in HORMIGON: return grupos
    for r in registros:
        grado = grado_normalizado(r.get('grado'))
        g = grupos.setdefault(grado, {'cantidad':0., 'volumen':0., 'suministro':0.})
        g['cantidad'] += r['neto']
        g['volumen'] += r['aux']['Hormigón neto (m³)'] if codigo=='2.14' else r['neto']
        g['suministro'] += r['aux']['Hormigón con pérdida (m³)']
    return grupos
