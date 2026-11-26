from partidas.calculos_trazado import calcular_sector
from partidas.calculos_terminaciones_instalaciones import calcular,CAMPOS

DESTINOS={'1.1':'Trazado y niveles','4.4':'Cielo','4.6':'Cerámica de piso','4.7':'Guardapolvos','4.8':'Cornisas','5.2':'Agua potable','5.3':'Alcantarillado','5.4':'Artefactos sanitarios','5.1':'Puntos eléctricos'}

def preparar(r,codigo,factor,nombre,especificacion=''):
    if factor<=0: raise ValueError('Escala inválida')
    if codigo in ('1.1','4.4','4.6'):
        if not r['rect']: raise ValueError('Se requiere un rectángulo cerrado.')
        l,a=[x*factor for x in r['lados'][:2]]
        if codigo=='1.1': return 'trazado_1_1','sectores',calcular_sector(nombre,1,l,a,0.)
        v={'largo':l,'ancho':a}
    elif codigo in ('4.7','4.8','5.2','5.3'):
        if r['tipo']=='INSERT' or r['longitud']<=0: raise ValueError('Se requiere línea o polilínea medible.')
        v={'largo':r['longitud']*factor}
    elif codigo in ('5.1','5.4'):
        if r['tipo']!='INSERT': raise ValueError('Se requiere un bloque DXF.')
        v={}
    else: raise ValueError('Partida no disponible para importación.')
    valores={k:v.get(k,default) for k,_,default,_ in CAMPOS[codigo]}
    return 'terminaciones_instalaciones_'+codigo,'elementos',calcular(codigo,nombre,1,valores,especificacion)
