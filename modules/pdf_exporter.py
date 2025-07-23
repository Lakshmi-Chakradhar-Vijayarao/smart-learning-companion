# ✅ pdf_exporter.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_pdf(content: str, filename="report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    lines = content.split('\n')
    y = height - 40
    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= 15
    c.save()
    return filename