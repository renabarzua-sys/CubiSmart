"""Metrado geométrico de techumbre. No dimensiona estructuras ni sistemas hidráulicos."""
from math import sqrt,ceil,isfinite
from partidas.catalogo import CATEGORIAS
CAT={c:(n,u) for c,n,u in CATEGORIAS['Techumbre y cubierta']}
L=('largo','Longitud (m)',0.,True); A=('ancho','Ancho horizontal del faldón (m)',0.,True)
I=('pendiente','Pendiente del faldón (%) — 0 si ancho ya inclinado',0.,False)
D=('descuento','Descuento total sobre superficie inclinada (m²)',0.,False)
P=('perdida','Recargo de suministro (%)',0.,False)
SUP=(L,A,I,D,P)
CAMPOS={'3.1':(L,('ancho','Ancho en planta (m)',0.,True),('descuento','Descuento total en planta (m²)',0.,False),('cerchas','Cerchas por sector según plano',0.,False),('madera_cercha','Longitud desarrollada de madera por cercha (m)',0.,False),('soleras','Longitud de soleras por sector (m)',0.,False),P),
'3.2':(L,('filas','Número de líneas de costaneras por sector',1.,True),('descuento','Descuento total de longitud (m)',0.,False),P,('pieza','Largo comercial de pieza (m; 0 = omitir estimación)',0.,False)),
'3.3':SUP+(('util','Superficie útil por placa (m²; 0 = omitir estimación)',0.,False),),
'3.4':SUP+(('util','Superficie útil por rollo descontando traslapos (m²; 0 = omitir)',0.,False),),
'3.5':SUP+(('util','Superficie útil por pieza o plancha (m²; 0 = omitir)',0.,False),),
'3.6':(L,P,('pieza','Largo comercial útil de tramo (m; 0 = omitir)',0.,False)),
'3.7':(L,('extra','Longitud adicional por bajada (m)',0.,False),P,('pieza','Largo comercial útil de tubo (m; 0 = omitir)',0.,False))}
GUIA={
'3.1':('Superficie de referencia en planta según alcance contractual. Despiece de cerchas y soleras ingresado desde plano, no calculado estructuralmente.','N × L × ancho − descuento; madera = N × (cerchas × longitud desarrollada + soleras)','madera o perfiles según proyecto, conectores, fijaciones, mano de obra'),
'3.2':('Registra líneas iguales por sector; usa longitud real de cada línea según plano. Sección y material configurables.','N × L × líneas − descuento','costaneras, fijaciones, mano de obra'),
'3.3':('Registra faldones rectangulares por separado. Ingresa pendiente en porcentaje y ancho horizontal, o ancho inclinado con pendiente cero. Superficie útil de placa según despiece.','N × L × ancho × √(1 + (pendiente/100)²) − descuento','placas OSB según espesor de proyecto, tornillos, mano de obra'),
'3.4':('Superficie inclinada; superficie útil de rollo debe contemplar traslapos. No duplicar traslapos en recargo.','N × L × ancho × √(1 + (pendiente/100)²) − descuento','fieltro o membrana, fijaciones, sellos, mano de obra'),
'3.5':('Superficie inclinada de cada faldón. Área útil de producto según fabricante; cortes y modulación requieren despiece.','N × L × ancho × √(1 + (pendiente/100)²) − descuento','cubierta según proyecto, fijaciones, cumbreras y remates según despiece'),
'3.6':('Longitud efectiva de canales según plano. Accesorios y capacidad hidráulica no se deducen de la longitud.','N × L','canales, soportes, uniones, tapas, mano de obra'),
'3.7':('Longitud desarrollada de cada bajada; agrega desplazamientos si no están incluidos en longitud principal.','N × (L + longitud adicional)','tubos, codos, abrazaderas, uniones, mano de obra')}

def calcular(codigo,nombre,cantidad,valores,especificacion=None):
    if codigo not in CAT or not nombre.strip() or not isfinite(cantidad) or cantidad<1 or int(cantidad)!=cantidad: raise ValueError('Nombre o cantidad inválidos.')
    v={k:float(valores[k]) for k,_,_,_ in CAMPOS[codigo]}
    for k,et,_,pos in CAMPOS[codigo]:
        if not isfinite(v[k]) or v[k]<0 or (pos and v[k]==0): raise ValueError('Revisa: '+et)
    for k in ('cerchas','filas'):
        if k in v and int(v[k])!=v[k]: raise ValueError('La cantidad de cerchas o líneas debe ser entera.')
    n=int(cantidad); l=v['largo']; d=v.get('descuento',0); f=1+v.get('perdida',0)/100; aux={}
    if codigo=='3.1':
        bruto=n*l*v['ancho']; aux={'Cerchas (un)':n*v['cerchas'],'Madera de cerchas (m)':n*v['cerchas']*v['madera_cercha'],'Soleras (m)':n*v['soleras']}; aux['Madera total con recargo (m)']=(aux['Madera de cerchas (m)']+aux['Soleras (m)'])*f
    elif codigo=='3.2': bruto=n*l*v['filas']
    elif codigo in ('3.3','3.4','3.5'):
        inclinado=v['ancho']*sqrt(1+(v['pendiente']/100)**2); bruto=n*l*inclinado; aux['Ancho inclinado (m)']=inclinado
    elif codigo=='3.6': bruto=n*l
    else: bruto=n*(l+v['extra'])
    neto=bruto-d
    if neto<=0 or not isfinite(neto): raise ValueError('La cantidad neta debe ser positiva y finita.')
    if codigo!='3.1':
        u=CAT[codigo][1]; aux[f'Suministro con recargo ({u})']=neto*f
        util=v.get('util',v.get('pieza',0))
        if util>0:
            q=neto*f/util
            if not isfinite(q): raise ValueError('Revisa el rendimiento comercial.')
            aux['Unidades comerciales estimadas (un)']=ceil(q)
    if not all(isfinite(x) and x>=0 for x in aux.values()): raise ValueError('Resultados no válidos.')
    return {'nombre':nombre.strip(),'cantidad':n,'valores':v,'bruto':bruto,'neto':neto,'aux':aux,'especificacion':str(especificacion or '').strip()}
