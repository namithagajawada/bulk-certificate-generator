
from app.services.certificate_service import (
    generate_certificate as real_generate_certificate,
)


def sample_request():
    return {
        "certificate_title": "Python Workshop",
        "organization": "ABC Institute",
        "recipients": [
            {"name": "Ananya Sharma", "email": "ananya@example.com"},
            {"name": "Rahul Verma", "email": "rahul@example.com"},
        ],
    }


def test_create_job_and_check_status(client):
    response = client.post("/api/jobs", json=sample_request())

    assert response.status_code == 201
    data = response.json()

    assert data["total_recipients"] == 2
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0
    assert data["status"] == "COMPLETED"

    job_id = data["job_id"]
    status_response = client.get(f"/api/jobs/{job_id}")

    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "COMPLETED"
    assert len(status_data["recipients"]) == 2
    assert all(
        recipient["status"] == "SUCCESS"
        for recipient in status_data["recipients"]
    )


def test_validation_rejects_empty_recipient_list(client):
    payload = {
        "certificate_title": "Python Workshop",
        "organization": "ABC Institute",
        "recipients": [],
    }

    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


def test_individual_certificate_download(client):
    response = client.post("/api/jobs", json=sample_request())
    job_id = response.json()["job_id"]

    status_response = client.get(f"/api/jobs/{job_id}")
    recipient_id = status_response.json()["recipients"][0]["recipient_id"]

    download = client.get(
        f"/api/recipients/{recipient_id}/certificate"
    )

    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")


def test_download_all_certificates_as_zip(client):
    response = client.post("/api/jobs", json=sample_request())
    job_id = response.json()["job_id"]

    download = client.get(f"/api/jobs/{job_id}/certificates.zip")

    assert download.status_code == 200
    assert download.headers["content-type"] == "application/zip"
    assert len(download.content) > 0


def test_missing_job_returns_404(client):
    response = client.get("/api/jobs/999999")

    assert response.status_code == 404


def test_one_failure_does_not_stop_other_certificates(
    client, monkeypatch
):
    def generate_with_one_failure(
        recipient_name,
        certificate_title,
        organization,
        output_path,
    ):
        if recipient_name == "Rahul Verma":
            raise RuntimeError("Simulated PDF generation failure")

        return real_generate_certificate(
            recipient_name=recipient_name,
            certificate_title=certificate_title,
            organization=organization,
            output_path=output_path,
        )

    monkeypatch.setattr(
        "app.services.job_service.generate_certificate",
        generate_with_one_failure,
    )

    response = client.post("/api/jobs", json=sample_request())

    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "PARTIAL"
    assert data["successful_count"] == 1
    assert data["failed_count"] == 1

    status_response = client.get(f"/api/jobs/{data['job_id']}")
    recipients = status_response.json()["recipients"]

    assert recipients[0]["status"] == "SUCCESS"
    assert recipients[1]["status"] == "FAILED"
    assert recipients[1]["error_message"] is not None

def test_whitespace_only_recipient_name_is_rejected(client):
    payload = {
        "certificate_title": "Python Workshop",
        "organization": "ABC Institute",
        "recipients": [{"name": "   "}],
    }

    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


def test_whitespace_only_title_is_rejected(client):
    payload = {
        "certificate_title": "   ",
        "organization": "ABC Institute",
        "recipients": [{"name": "Ananya Sharma"}],
    }

    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422


def test_invalid_email_is_rejected(client):
    payload = {
        "certificate_title": "Python Workshop",
        "organization": "ABC Institute",
        "recipients": [
            {"name": "Ananya Sharma", "email": "not-an-email"}
        ],
    }

    response = client.post("/api/jobs", json=payload)

    assert response.status_code == 422
