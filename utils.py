from reportlab.pdfgen import canvas
import StringIO


def compose_pdf(profile):
    output = StringIO.StringIO()
    p = canvas.Canvas(output)
    p.drawString(100, 100, profile['firstName'])
    p.showPage()
    p.save()
    pdf = output.getvalue()
    output.close()
    return pdf
