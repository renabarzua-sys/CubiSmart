"""CubiSmart: servicios.exportaciones."""
from servicios.base_datos import extras_leer
from servicios.estado import S
import streamlit as st

AVISO_EXPORTACION = 'Estimación geométrica simplificada; no acredita cumplimiento de NCh353. No incluye confinamientos, superposición de vanos ni relleno de perforaciones. Los resultados corresponden a muros guardados; dosificación no incluida.'

def filas_exportacion(muros):
    return [[n, r['memoria']['largo'], r['memoria']['alto'], r['superficie'], r['superficie_vanos'], r['superficie_neta'], r['volumen'], r['ladrillos_finales'], r['mortero_final']] for n,r in muros.items()]


def pasos_exportacion(r):
    m=r['memoria']
    return [
        ('Superficie bruta', f"{m['largo']:.6g} × {m['alto']:.6g}", r['superficie'], 'm²'),
        *[(f'Vano {i}', f'{a:.6g} × {h:.6g}', a*h, 'm²') for i,(a,h) in enumerate(m['vanos'],1)],
        ('Vanos totales', 'Suma de superficies de vanos', r['superficie_vanos'], 'm²'),
        ('Superficie neta', f"{r['superficie']:.8g} - {r['superficie_vanos']:.8g}", r['superficie_neta'], 'm²'),
        ('Volumen neto', f"{r['superficie_neta']:.8g} × {m['espesor']:.6g}", r['volumen'], 'm³'),
        ('Largo modular', f"{m['largo_ladrillo']:.6g} + {m['junta_mortero']:.6g}", m['largo_modular'], 'm'),
        ('Alto modular', f"{m['alto_ladrillo']:.6g} + {m['junta_mortero']:.6g}", m['alto_modular'], 'm'),
        ('Área modular', f"{m['largo_modular']:.6g} × {m['alto_modular']:.6g}", r['superficie_modular'], 'm²'),
        ('Ladrillos teóricos', f"{r['superficie_neta']:.8g} / {r['superficie_modular']:.8g}", m['cantidad_ladrillos'], 'un'),
        ('Ladrillos para compra', f"{m['cantidad_ladrillos']:.8g} × (1 + {m['porcentaje_perdida']:g}/100), entero superior", r['ladrillos_finales'], 'un'),
        ('Volumen del ladrillo', f"{m['largo_ladrillo']:g} × {m['alto_ladrillo']:g} × {m['ancho_ladrillo']:g}", m['volumen_ladrillo'], 'm³'),
        ('Volumen modular', f"{m['largo_modular']:g} × {m['alto_modular']:g} × {m['ancho_ladrillo']:g}", m['volumen_modular'], 'm³'),
        ('Mortero por módulo', f"{m['volumen_modular']:.9g} - {m['volumen_ladrillo']:.9g}", m['mortero_por_modulo'], 'm³'),
        ('Mortero sin pérdidas', f"{m['mortero_por_modulo']:.9g} × {m['cantidad_ladrillos']:.8g}", r['mortero'], 'm³'),
        ('Mortero con pérdidas', f"{r['mortero']:.9g} × (1 + {m['porcentaje_perdida_mortero']:g}/100)", r['mortero_final'], 'm³'),
        ('Mortero en litros', f"{r['mortero_final']:.9g} × 1000", r['mortero_final']*1000, 'L'),
    ]


def exportar_excel(proyecto, muros, responsable='', ubicacion='', plano=''):
    from io import BytesIO
    from datetime import date
    import xlsxwriter
    out=BytesIO()
    with xlsxwriter.Workbook(out, {'in_memory':True,'strings_to_formulas':False,'strings_to_urls':False}) as wb:
        h=wb.add_format({'bold':True,'bg_color':'#127566','font_color':'white','text_wrap':True,'valign':'vcenter'})
        t=wb.add_format({'bold':True,'font_size':18,'font_color':'#163B39'})
        n=wb.add_format({'num_format':'0.0000','font_color':'#163B39'})
        entero=wb.add_format({'num_format':'0'})
        total=wb.add_format({'bold':True,'bg_color':'#DDF3EB','num_format':'0.0000'})
        total_un=wb.add_format({'bold':True,'bg_color':'#DDF3EB','num_format':'0'})
        wrap=wb.add_format({'text_wrap':True,'valign':'top'})
        ws=wb.add_worksheet('Cubicación'); ws.hide_gridlines(2)
        ws.set_column(0,0,32); ws.set_column(1,8,17)
        ws.merge_range(0,0,0,8,'CubiSmart | Cubicación de albañilería',t)
        for i,(k,v) in enumerate([('Proyecto',proyecto),('Responsable',responsable),('Ubicación',ubicacion),('Plano / referencia',plano),('Fecha',date.today().isoformat())],1):
            ws.write(i,0,k); ws.merge_range(i,1,i,8,v or 'No indicado')
        headers=['Muro','Largo (m)','Alto (m)','Bruta (m²)','Vanos (m²)','Neta (m²)','Volumen (m³)','Ladrillos (un)','Mortero (m³)']
        ws.write_row(7,0,headers,h); ws.set_row(7,32)
        filas=filas_exportacion(muros)
        for i,f in enumerate(filas,8):
            ws.write_string(i,0,f[0]);
            for j,v in enumerate(f[1:],1): ws.write_number(i,j,v,entero if j==7 else n)
        fin=8+len(filas); ws.write(fin,0,'TOTAL',total)
        for j in range(3,9):
            col=chr(65+j); ws.write_formula(fin,j,f'=SUM({col}9:{col}{fin})',total_un if j==7 else total,sum(f[j] for f in filas))
        ws.merge_range(fin+2,0,fin+2,8,AVISO_EXPORTACION,wrap); ws.set_row(fin+2,42)
        ws.freeze_panes(8,1); ws.autofilter(7,0,fin-1,8)
        mem=wb.add_worksheet('Memoria'); mem.hide_gridlines(2); mem.set_column(0,0,28); mem.set_column(1,1,30); mem.set_column(2,2,65); mem.set_column(3,3,18); mem.set_column(4,4,12)
        mem.write_row(0,0,['Muro','Operación','Desarrollo','Resultado','Unidad'],h); mem.freeze_panes(1,1)
        formato_mem=wb.add_format({'num_format':'0.00000000'})
        i=1
        for nombre,r in muros.items():
            for paso,op,val,u in pasos_exportacion(r):
                mem.write_row(i,0,[nombre,paso,op]); mem.write_number(i,3,val,formato_mem); mem.write(i,4,u); i+=1
        mem.autofilter(0,0,i-1,4)
    return out.getvalue()


def exportar_pdf(proyecto, muros, responsable='', ubicacion='', plano=''):
    from io import BytesIO
    from datetime import date
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=42)
    styles=getSampleStyleSheet(); styles['Title'].textColor=colors.HexColor('#163B39'); styles['Heading2'].textColor=colors.HexColor('#127566')
    small=ParagraphStyle('Small',parent=styles['BodyText'],fontSize=8,leading=11,wordWrap='CJK')
    white=ParagraphStyle('White',parent=small,textColor=colors.white)
    def para(x,sty=small): return Paragraph(escape(str(x)),sty)
    def tabla(headers,rows,widths):
        data=[[para(x,white) for x in headers]]+[[para(x) for x in row] for row in rows]
        tb=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT'); tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#127566')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EAF7F1')]),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)])); return tb
    story=[para('CubiSmart | Memoria de cubicación',styles['Title'])]
    for k,v in [('Proyecto',proyecto),('Responsable',responsable),('Ubicación',ubicacion),('Plano / referencia',plano),('Fecha',date.today().isoformat())]: story.append(para(f'{k}: {v or "No indicado"}',styles['BodyText']))
    story += [Spacer(1,12),para('Resumen general',styles['Heading2'])]
    filas=filas_exportacion(muros); rows=[[f[0],f'{f[3]:.2f}',f'{f[4]:.2f}',f'{f[5]:.2f}',f'{f[6]:.3f}',str(f[7]),f'{f[8]:.4f}'] for f in filas]
    rows.append(['TOTAL']+[f'{sum(f[j] for f in filas):.{p}f}' for j,p in [(3,2),(4,2),(5,2),(6,3),(7,0),(8,4)]])
    story += [tabla(['Muro','Bruta m²','Vanos m²','Neta m²','Vol. m³','Ladrillos un','Mortero m³'],rows,[139,61,61,61,61,65,75]),Spacer(1,12),para(AVISO_EXPORTACION)]
    for nombre,r in muros.items():
        story += [PageBreak(),para('Muro: '+nombre,styles['Heading2']),tabla(['Operación','Desarrollo','Resultado','Unidad'],[[a,b,f'{c:.8g}',d] for a,b,c,d in pasos_exportacion(r)],[135,245,100,43]),Spacer(1,10),para('Las operaciones se muestran redondeadas; los resultados se calculan con los valores originales.')]
    def pie(canvas,doc):
        canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor('#163B39')); canvas.drawString(36,23,'CubiSmart | Estimación de materiales'); canvas.drawRightString(A4[0]-36,23,f'Página {doc.page}')
    doc.build(story,onFirstPage=pie,onLaterPages=pie); return out.getvalue()


def mostrar_exportacion():
    with st.container(key="exportacion_panel"):
        st.markdown('## 📄 Exportar cubicación')
        st.caption('Proyecto: '+S.proyecto_nombre)
        if not S.muros_guardados:
            st.info('Guarda al menos un muro para exportar.'); return
        st.caption('Solo se incluyen muros guardados, no los borradores.')
        alcance=st.radio('Alcance',['Proyecto completo','Un muro'],key='exp_alcance')
        muros=S.muros_guardados
        if alcance=='Un muro':
            elegido=st.selectbox('Muro a exportar',list(muros),key='exp_muro'); muros={elegido:muros[elegido]}
        f=extras_leer(S.proyecto_id).get('ficha',{})
        responsable=st.text_input('Profesional responsable (opcional)',value=f.get('responsable',''),key='exp_resp')
        ubicacion=st.text_input('Ubicación (opcional)',value=', '.join(x for x in [f.get('direccion',''),f.get('comuna','')] if x),key='exp_ubi')
        plano=st.text_input('Plano o referencia (opcional)',value=f.get('plano',''),key='exp_plano')
        st.caption(f'{len(muros)} muro(s) incluidos. {AVISO_EXPORTACION}')
        try:
            excel=exportar_excel(S.proyecto_nombre,muros,responsable,ubicacion,plano)
            pdf=exportar_pdf(S.proyecto_nombre,muros,responsable,ubicacion,plano)
        except ImportError:
            st.error('Instala las dependencias: py -m pip install xlsxwriter reportlab'); return
        a,b=st.columns(2)
        a.download_button('📊 Descargar Excel',excel,'CubiSmart_cubicacion.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        b.download_button('📄 Descargar PDF',pdf,'CubiSmart_memoria.pdf','application/pdf',use_container_width=True)


def costos_exportar(titulo, filas, subtotal, iva, total):
    from io import BytesIO
    import xlsxwriter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from xml.sax.saxutils import escape
    out=BytesIO()
    with xlsxwriter.Workbook(out,{'in_memory':True,'strings_to_formulas':False,'strings_to_urls':False}) as w:
        ws=w.add_worksheet('Costos'); ws.set_column(0,0,48); ws.set_column(1,4,19)
        h=w.add_format({'bg_color':'#127566','font_color':'white','bold':True}); n=w.add_format({'num_format':'#,##0.00'})
        ws.write(0,0,titulo); ws.write_row(2,0,['Recurso','Unidad','Cantidad','Precio neto','Total neto'],h)
        for i,f in enumerate(filas,3):
            ws.write_row(i,0,f[:2])
            for j,x in enumerate(f[2:],2):
                ws.write_number(i,j,x,n)
        for i,(k,v) in enumerate([('Subtotal',subtotal),('IVA',iva),('Total',total)],len(filas)+4): ws.write(i,0,k,h); ws.write_number(i,4,v,n)
    pdf=BytesIO(); styles=getSampleStyleSheet(); body=styles['BodyText']; body.fontSize=9
    rows=[['Recurso','Unidad','Cantidad','Precio neto','Total neto']]+[[Paragraph(escape(str(f[0])),body),f[1],f'{f[2]:.4f}',f'{f[3]:,.2f}',f'{f[4]:,.2f}'] for f in filas]+[[k,'','','',f'{v:,.2f}'] for k,v in [('Subtotal',subtotal),('IVA',iva),('Total',total)]]
    tb=Table(rows,colWidths=[170,48,78,85,85],repeatRows=1); tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#127566')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EAF7F1')])]))
    SimpleDocTemplate(pdf).build([Paragraph(escape(titulo),styles['Title']),Spacer(1,12),tb,Spacer(1,12),Paragraph('Estimación referencial. Valores en CLP; no acredita cumplimiento normativo.',body)])
    return out.getvalue(),pdf.getvalue()


