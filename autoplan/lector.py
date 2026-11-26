"""Extracción geométrica local. No interpreta automáticamente la función constructiva."""
import math, io, tempfile
from pathlib import Path

UNIDADES={1:0.0254,2:0.3048,4:0.001,5:0.01,6:1.,7:1000.}

def fila(id,capa,tipo,puntos,cerrado=False,bloque='',rect=False):
    p=[(float(xy[0]),float(xy[1])) for xy in puntos]
    if not p or not all(math.isfinite(v) for xy in p for v in xy): raise ValueError('Geometría inválida')
    pares=list(zip(p,p[1:]))+([(p[-1],p[0])] if cerrado else [])
    largo=sum(math.dist(a,b) for a,b in pares)
    area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in pares))/2 if cerrado else 0.
    lados=[math.dist(a,b) for a,b in pares]
    if cerrado and len(p)==4 and min(lados)>0:
        rect=all(abs((p[(i+1)%4][0]-p[i][0])*(p[(i+2)%4][0]-p[(i+1)%4][0])+(p[(i+1)%4][1]-p[i][1])*(p[(i+2)%4][1]-p[(i+1)%4][1]))<1e-7*lados[i]*lados[(i+1)%4] for i in range(4))
    return dict(id=str(id),capa=str(capa),tipo=tipo,puntos=p,cerrado=cerrado,bloque=bloque,longitud=largo,area=area,rect=rect,lados=lados)

def dxf(datos, extension='dxf'):
    import ezdxf
    from ezdxf import recover
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/('plano.'+extension); p.write_bytes(datos)
        if extension=='dwg':
            from ezdxf.addons import odafc
            if not odafc.is_installed(): raise ValueError('Instala ODA File Converter o exporta el DWG a DXF desde AutoCAD.')
            doc=odafc.readfile(p)
        else:
            doc=ezdxf.readfile(p)
        filas=[]; omitidos={}
        for e in doc.modelspace():
            t=e.dxftype(); k=e.dxf.handle; c=e.dxf.layer
            try:
                if t=='LINE' and abs(e.dxf.start.z-e.dxf.end.z)<1e-8: r=fila(k,c,t,[e.dxf.start.xy,e.dxf.end.xy])
                elif t=='LWPOLYLINE' and not e.has_arc and e.dxf.extrusion.isclose((0,0,1)):
                    r=fila(k,c,t,list(e.get_points('xy')),e.closed)
                elif t=='INSERT' and e.mcount==1: r=fila(k,c,t,[e.dxf.insert.xy],bloque=e.dxf.name)
                else: omitidos[t]=omitidos.get(t,0)+1; continue
                filas.append(r)
            except (ValueError,TypeError,AttributeError): omitidos[t]=omitidos.get(t,0)+1
            if len(filas)>30000: raise ValueError('Plano demasiado complejo; exporta un sector con menos de 30.000 entidades.')
        return filas,UNIDADES.get(doc.units),omitidos

def pdf(datos,pagina):
    import fitz
    with fitz.open(stream=datos,filetype='pdf') as doc:
        if doc.is_encrypted: raise ValueError('PDF protegido no compatible.')
        page=doc[pagina]; filas=[]; omitidos={}
        for i,path in enumerate(page.get_drawings()):
            for j,item in enumerate(path['items']):
                t=item[0]; k=f'{i}:{j}'
                if t=='l': r=fila(k,'PDF vectorial','LINE',[item[1],item[2]])
                elif t=='re':
                    z=item[1]; r=fila(k,'PDF vectorial','RECT',[(z.x0,z.y0),(z.x1,z.y0),(z.x1,z.y1),(z.x0,z.y1)],True)
                else: omitidos[t]=omitidos.get(t,0)+1; continue
                filas.append(r)
                if len(filas)>30000: raise ValueError('Página demasiado compleja.')
        return filas,omitidos,page.get_pixmap(matrix=fitz.Matrix(0.8,0.8),alpha=False).tobytes('png')
