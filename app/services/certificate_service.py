
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def generate_certificate(
    recipient_name: str,
    certificate_title: str,
    organization: str,
    output_path: str | Path,
) -> str:
    """
    Generate a personalized PDF certificate.

    Returns the path of the generated PDF.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(
        str(output_file),
        pagesize=(page_width, page_height),
    )

    # White background
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Outer and inner borders
    pdf.setStrokeColor(colors.HexColor("#17365D"))
    pdf.setLineWidth(5)
    pdf.rect(22, 22, page_width - 44, page_height - 44)

    pdf.setStrokeColor(colors.HexColor("#C49A45"))
    pdf.setLineWidth(1.5)
    pdf.rect(32, 32, page_width - 64, page_height - 64)

    center_x = page_width / 2

    # Organization
    pdf.setFillColor(colors.HexColor("#17365D"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawCentredString(
        center_x, page_height - 100, organization
    )

    # Certificate heading
    pdf.setFillColor(colors.HexColor("#C49A45"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        center_x, page_height - 155, "CERTIFICATE"
    )

    pdf.setFillColor(colors.HexColor("#17365D"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawCentredString(
        center_x, page_height - 185, "OF ACHIEVEMENT"
    )

    # Description
    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        center_x, page_height - 235,
        "This certificate is proudly presented to",
    )

    # Recipient name
    pdf.setFillColor(colors.HexColor("#17365D"))
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawCentredString(
        center_x, page_height - 285, recipient_name
    )

    # Certificate details
    pdf.setStrokeColor(colors.HexColor("#C49A45"))
    pdf.setLineWidth(1)
    pdf.line(
        center_x - 150, page_height - 300,
        center_x + 150, page_height - 300,
    )

    pdf.setFillColor(colors.HexColor("#444444"))
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        center_x, page_height - 335,
        f"for successfully completing {certificate_title}",
    )

    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        center_x, page_height - 360,
        f"Issued on {date.today().strftime('%d %B %Y')}",
    )

    # Signature placeholder
    pdf.setStrokeColor(colors.HexColor("#777777"))
    pdf.line(
        center_x - 75, 85, center_x + 75, 85
    )
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(center_x, 68, "Authorized Signatory")

    pdf.save()
    return str(output_file)
