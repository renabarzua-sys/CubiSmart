"""Cubicación geométrica; no dimensiona instalaciones ni prescribe materiales."""
from math import ceil,isfinite
from partidas.catalogo import CATEGORIAS
CAT={c:(n,u) for grupo in ('Terminaciones','Instalaciones') for c,n,u in CATEGORIAS[grupo]}
L=('largo','Longitud (m)',0.,True); A=('ancho','Ancho o altura (m)',0.,True)
D=('descuento','Descuento total (m²)',0.,False); P=('perdida','Recargo de suministro (%)',0.,False)
C=('caras','Caras iguales por elemento',1.,True)
U=('util','Superficie útil por unidad comercial (m²; 0 = omitir)',0.,False)
E=('espesor','Espesor de capa (m; 0 = omitir volumen)',0.,False)
R=('rendimiento','Rendimiento del producto (m²/L por mano; 0 = omitir)',0.,False)
DL=('descuento','Descuento total (m)',0.,False)
PC=('pieza','Longitud útil comercial (m; 0 = omitir)',0.,False)
CAMPOS={
'4.1':(L,A,C,D,E,P),'4.2':(L,A,C,D,E,P),
'4.3':(L,A,C,D,P,U),'4.4':(L,A,D,P,U),'4.5':(L,A,D,E,P,U),
'4.6':(L,A,D,P,U,('adhesivo','Consumo adhesivo (kg/m²; 0 = omitir)',0.,False),('frague','Consumo fragüe (kg/m²; 0 = omitir)',0.,False)),
'4.7':(L,DL,P,PC),'4.8':(L,DL,P,PC),
'4.9':(L,A,C,D,('manos','Cantidad de manos',1.,True),R,P),
'4.10':(A,('alto','Altura de puerta (m)',0.,True)),
'4.11':(A,('alto','Altura de ventana (m)',0.,True)),
'5.1':(('cable','Longitud total de conductores por punto (m; 0 = omitir)',0.,False),('ducto','Longitud de ducto por punto (m; 0 = omitir)',0.,False),P),
'5.2':(L,DL,P,PC),'5.3':(L,DL,P,PC),'5.4':()}
GUIA={
'4.1':('Superficie de estuco exterior según alcance; descuenta vanos que correspondan. Espesor según proyecto.','N × L × ancho/alto × caras − descuento','mortero, agua, mano de obra, equipos'),
'4.2':('Superficie de estuco interior; registra caras y descuentos según planos.','N × L × ancho/alto × caras − descuento','mortero, agua, mano de obra'),
'4.3':('Registra cada tipo de placa y número de caras; considera modulación y cortes.','N × L × alto × caras − descuento','placas, tornillos, cinta, pasta de juntas'),
'4.4':('Usa dimensiones reales del cielo y registra sectores sin solapamiento.','N × L × ancho − descuento','placas, fijaciones, perfiles según alcance'),
'4.5':('Usa superficie real de instalación, horizontal o inclinada según plano. Espesor y producto según especificaciones.','N × L × ancho − descuento','aislante, fijaciones, barreras según proyecto'),
'4.6':('Superficie de piso; usa rendimiento útil y consumos del fabricante.','N × L × ancho − descuento','cerámica, adhesivo, fragüe, separadores'),
'4.7':('Registra perímetros o tramos; descuenta puertas cuando corresponda.','N × L − descuento','guardapolvos, fijaciones, adhesivo'),
'4.8':('Registra longitudes reales de encuentros que reciben cornisa.','N × L − descuento','cornisas, adhesivo, fijaciones'),
'4.9':('Superficie neta pintada; manos y rendimiento según producto y soporte.','N × L × ancho/alto × caras − descuento; litros = superficie × manos / rendimiento','pintura, imprimante, lijas, herramientas'),
'4.10':('Cuenta puertas iguales por modelo y dimensiones; registra marco y herrajes en APU.','N unidades','puerta, marco, bisagras, cerradura'),
'4.11':('Cuenta ventanas iguales por modelo y dimensiones; no dimensiona vidrio ni perfiles.','N unidades','ventana, fijaciones, sellos'),
'5.1':('Cuenta puntos por tipo según plano eléctrico. Longitudes opcionales del despiece; no dupliques tramos compartidos. No dimensiona circuitos.','N puntos','conductores, ductos, cajas, mecanismos, mano de obra'),
'5.2':('Longitud desarrollada de tuberías por material y diámetro según plano. No calcula diámetros hidráulicos.','N × L − descuento','tuberías, accesorios, válvulas, fijaciones'),
'5.3':('Longitud real desarrollada por diámetro y material, incluyendo inclinación cuando corresponda. No dimensiona redes ni pendientes.','N × L − descuento','tuberías, fittings, registros, fijaciones'),
'5.4':('Cuenta artefactos por tipo/modelo; accesorios y conexiones según proyecto.','N unidades','artefactos, grifería, sifones, conexiones')}

def calcular(codigo,nombre,cantidad,valores,especificacion=None):
    if codigo not in CAT or not nombre.strip() or not isfinite(cantidad) or cantidad<1 or int(cantidad)!=cantidad: raise ValueError('Nombre o cantidad inválidos.')
    v={k:float(valores[k]) for k,_,_,_ in CAMPOS[codigo]}
    for k,et,_,pos in CAMPOS[codigo]:
        if not isfinite(v[k]) or v[k]<0 or (pos and v[k]==0): raise ValueError('Revisa: '+et)
    for k in ('caras','manos'):
        if k in v and int(v[k])!=v[k]: raise ValueError('Caras y manos deben ser cantidades enteras.')
    n=int(cantidad); u=CAT[codigo][1]; aux={}; f=1+v.get('perdida',0)/100
    bruto=n*v.get('largo',1)*v.get('ancho',1)*v.get('caras',1) if u=='m²' else n*v['largo'] if u=='ml' else n
    neto=bruto-v.get('descuento',0)
    if not isfinite(neto) or neto<=0: raise ValueError('La cantidad neta debe ser positiva y finita.')
    if u in ('m²','ml') and codigo!='4.9':
        aux[f'Suministro con recargo ({u})']=neto*f
        util=v.get('util',v.get('pieza',0))
        if util>0: aux['Unidades comerciales estimadas (un)']=ceil(neto*f/util)
    if v.get('espesor',0)>0: aux['Volumen neto (m³)']=neto*v['espesor']; aux['Volumen con recargo (m³)']=neto*v['espesor']*f
    if codigo=='4.6':
        for k,et in [('adhesivo','Adhesivo (kg)'),('frague','Fragüe (kg)')]:
            if v[k]>0: aux[et]=neto*v[k]
    if codigo=='4.9':
        aux['Superficie acumulada de manos (m²)']=neto*v['manos']
        if v['rendimiento']>0: aux['Pintura con recargo (L)']=neto*v['manos']/v['rendimiento']*f
    if codigo in ('4.10','4.11'): aux['Superficie nominal (m²)']=n*v['ancho']*v['alto']
    if codigo=='5.1':
        aux['Conductores con recargo (m)']=n*v['cable']*f; aux['Ductos con recargo (m)']=n*v['ducto']*f
    if not all(isfinite(x) and x>=0 for x in aux.values()): raise ValueError('Resultados inválidos.')
    return dict(nombre=nombre.strip(),cantidad=n,valores=v,bruto=bruto,neto=neto,aux=aux,especificacion=str(especificacion or '').strip())
