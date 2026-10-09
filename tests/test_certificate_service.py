
from pathlib import Path

from app.services.certificate_service import generate_certificate


def test_generate_certificate_creates_pdf(tmp_path):
    output_path = tmp_path / "test_certificate.pdf"

    result = generate_certificate(
        recipient_name="Ananya Sharma",
        certificate_title="Python Workshop",
        organization="ABC Institute",
        output_path=output_path,
    )

    assert Path(result).exists()
    assert Path(result).stat().st_size > 0

    with open(result, "rb") as pdf_file:
        assert pdf_file.read(4) == b"%PDF"
