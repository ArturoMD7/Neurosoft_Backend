from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
import os
import json

from resultados.models import Resultado
from pacientes.models import Paciente

def generar_informe_pdf(request, resultado_id):
    try:
        resultado = Resultado.objects.get(id=resultado_id)
        paciente = resultado.paciente

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        left_margin = 3 * cm
        top_margin = height - 3 * cm

        # === Encabezado ===
        p.setFont("Helvetica-Bold", 16)
        p.drawString(left_margin, top_margin, "Informe Médico de NeuroSoft")
        p.setStrokeColor(colors.darkblue)
        p.setLineWidth(2)
        p.line(left_margin, top_margin - 10, width - left_margin, top_margin - 10)

        # === Logo ===
        logo_path = r'C:\ruta\al\logo.jpg'
        if os.path.exists(logo_path):
            p.drawImage(logo_path, width - 100 - 2*cm, height - 100 - 2*cm, width=100, height=100, preserveAspectRatio=True, mask='auto')

        # === Datos del paciente ===
        y = top_margin - 50
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Datos del paciente:")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(left_margin, y, f"Nombre: {paciente.nombre} {paciente.apellido_paterno} {paciente.apellido_materno}")
        y -= 18
        p.drawString(left_margin, y, f"CURP: {paciente.curp}")
        y -= 18
        p.drawString(left_margin, y, f"NSS: {paciente.nss}")
        y -= 18
        p.drawString(left_margin, y, f"Fecha del estudio: {resultado.fecha_estudio.strftime('%d/%m/%Y')}")
        y -= 18
        p.drawString(left_margin, y, f"Fecha de resultado: {resultado.fecha_resultado.strftime('%d/%m/%Y')}")
        y -= 30

        # === Estado y diagnóstico ===
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Detalles del estudio:")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(left_margin, y, f"Estado del estudio: {resultado.estado_estudio}")
        y -= 18
        p.drawString(left_margin, y, f"Predicción de IA: {resultado.prediccion_ia}")
        y -= 18
        p.drawString(left_margin, y, f"Precisión del modelo: {resultado.precision_porcentaje}")
        y -= 30

        # === Imagen del estudio ===
        if resultado.imagen_estudio and os.path.exists(resultado.imagen_estudio.path):
            img_w = 400
            img_h = 300
            img_x = (width - img_w) / 2
            img_y = y - img_h
            p.drawImage(resultado.imagen_estudio.path, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
            y = img_y - 40

        # === Resumen de la predicción ===
        if resultado.resumen_prediccion:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(left_margin, y, "Resumen de la predicción:")
            y -= 20
            p.setFont("Helvetica", 11)
            for linea in resultado.resumen_prediccion.splitlines():
                p.drawString(left_margin, y, linea)
                y -= 15

        # === Probabilidades JSON ===
        if resultado.probabilidades:
            try:
                probabilidades = json.loads(resultado.probabilidades)
                y -= 20
                p.setFont("Helvetica-Bold", 12)
                p.drawString(left_margin, y, "Probabilidades detalladas:")
                y -= 20
                p.setFont("Helvetica", 11)
                for clave, valor in probabilidades.items():
                    p.drawString(left_margin, y, f"{clave}: {valor:.2%}")
                    y -= 15
            except json.JSONDecodeError:
                pass

        # === Pie de página ===
        p.setFont("Helvetica-Oblique", 9)
        p.setFillColor(colors.grey)
        p.drawString(left_margin, 2 * cm, "Generado automáticamente por NeuroSoft")
        p.setFillColor(colors.black)

        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="reporte_{resultado.id}.pdf"'
        })

    except Resultado.DoesNotExist:
        return HttpResponse("Resultado no encontrado", status=404)
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)