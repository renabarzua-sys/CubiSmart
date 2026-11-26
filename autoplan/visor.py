"""Herramientas de vista y selección; no asignan significado constructivo."""
import math

def limites(filas):
    return (min(x for r in filas for x,y in r['puntos']), max(x for r in filas for x,y in r['puntos']), min(y for r in filas for x,y in r['puntos']), max(y for r in filas for x,y in r['puntos']))

def sector(filas, caja):
    x0,x1,y0,y1=caja
    return [r for r in filas if all(x0<=x<=x1 and y0<=y<=y1 for x,y in r['puntos'])]

def sin_duplicados(filas):
    vistos=set(); out=[]
    for r in filas:
        p=tuple(r['puntos'])
        if r['cerrado']:
            variantes=[s[i:]+s[:i] for s in (p,p[::-1]) for i in range(len(s))] if len(p)<=100 else [p,p[::-1]]
            forma=min(variantes)
        else: forma=min(p,p[::-1])
        k=(r['capa'],r['tipo'],r['cerrado'],r['bloque'],forma)
        if k not in vistos: out.append(r); vistos.add(k)
    return out

def imagen_pdf(datos,pagina,caja):
    import fitz
    with fitz.open(stream=datos,filetype='pdf') as doc:
        page=doc[pagina]
        x0,x1,y0,y1=caja
        clip=fitz.Rect(x0,y0,x1,y1)&page.rect
        if clip.is_empty: raise ValueError('Sector vacío')
        zoom=min(3,1600/max(clip.width,clip.height))
        return page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=clip,alpha=False).tobytes('png')
