from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
import os
from pacientes.models import Paciente

def generar_informe_pdf(request, resultado_id):
    try:
        paciente = Paciente.objects.get(id=resultado_id)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        left_margin = 3 * cm
        top_margin = height - 3 * cm

        # === Título ===
        p.setFont("Helvetica-Bold", 16)
        p.drawString(left_margin, top_margin, "Informe Médico de NeuroSoft")
        p.setStrokeColor(colors.darkblue)
        p.setLineWidth(2)
        p.line(left_margin, top_margin - 10, width - left_margin, top_margin - 10)

        # === Logo en la esquina superior derecha ===
        logo_path = r'C:\Users\jhern\OneDrive\Escritorio\neurosoft\Neurosoft_Backend\NeuroSoft\media\resultados\imagenes\logoNeuroSoft.jpg'
        if os.path.exists(logo_path):
            logo_width = 100
            logo_height = 100
            logo_x = width - logo_width - 2 * cm  # margen derecho
            logo_y = height - logo_height - 2 * cm  # arriba
            p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

        # === Datos del paciente ===
        y = top_margin - 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Datos del paciente:")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(left_margin, y, f"ID Estudio: {paciente.id}")
        y -= 18
        p.drawString(left_margin, y, f"Nombre completo: {paciente.nombre} {paciente.apellido_paterno} {paciente.apellido_materno}")
        y -= 18
        p.drawString(left_margin, y, f"CURP: {paciente.curp}")
        y -= 18
        p.drawString(left_margin, y, f"NSS: {paciente.nss}")

        # === Imagen del cerebro centrada ===
        y -= 50  # Espacio antes de la imagen
        cerebro_path = r'C:\Users\jhern\OneDrive\Escritorio\neurosoft\Neurosoft_Backend\NeuroSoft\media\resultados\imagenes\resultado_12_CcUQpJ4.png'
        if os.path.exists(cerebro_path):
            cerebro_width = 400
            cerebro_height = 300
            cerebro_x = (width - cerebro_width) / 2
            cerebro_y = y - cerebro_height
            p.drawImage(cerebro_path, cerebro_x, cerebro_y, width=cerebro_width, height=cerebro_height, preserveAspectRatio=True)
            y = cerebro_y - 40  # Espacio debajo de la imagen antes del texto

        # === Resultado del análisis ===
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Resultado del análisis:")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(left_margin, y, "Diagnóstico estimado: Muy probable ACV")

        # === Pie de página ===
        p.setFont("Helvetica-Oblique", 9)
        p.setFillColor(colors.grey)
        p.drawString(left_margin, 2 * cm, "Generado automáticamente por NeuroSoft")
        p.setFillColor(colors.black)

        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="reporte_{paciente.id}.pdf"'
        })

    except Paciente.DoesNotExist:
        return HttpResponse("Paciente no encontrado", status=404)
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)
