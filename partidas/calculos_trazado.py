from math import isfinite

def calcular_sector(nombre, cantidad, largo, ancho, descuento):
    if not nombre.strip(): raise ValueError('Ingresa el nombre del sector.')
    if not all(isfinite(v) for v in (cantidad,largo,ancho,descuento)) or cantidad < 1 or int(cantidad)!=cantidad or largo<=0 or ancho<=0 or descuento<0:
        raise ValueError('Revisa las dimensiones y cantidades.')
    bruto=cantidad*largo*ancho
    if not isfinite(bruto) or descuento>=bruto: raise ValueError('El descuento debe ser menor que la superficie bruta.')
    return dict(nombre=nombre.strip(),cantidad=int(cantidad),largo=largo,ancho=ancho,descuento=descuento,bruto=bruto,neto=bruto-descuento)

def calcular_recursos(area, recursos):
    if not isfinite(area) or area<0: raise ValueError('Superficie inválida.')
    filas=[]
    for r in recursos:
        if not r['nombre'].strip() or not r['unidad'].strip() or not all(isfinite(r[k]) and r[k]>=0 for k in ('consumo','precio','perdida')): raise ValueError('Revisa los recursos.')
        consumo=r['consumo']*(1+r['perdida']/100)
        filas.append(dict(**r, cantidad=area*consumo, costo_unitario=consumo*r['precio'], total=area*consumo*r['precio']))
    return filas
