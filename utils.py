from reportlab.pdfgen import canvas
import StringIO


def compose_pdf():
    output = StringIO.StringIO()
    p = canvas.Canvas(output)
    p.drawString(100, 100, 'Hello')
    p.showPage()
    p.save()
    pdf = output.getvalue()
    output.close()
    return pdf
