
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import GenerationJob
from app.services.certificate_service import generate_certificate


OUTPUT_DIR = Path("generated")


def process_generation_job(
    job_id: int,
    db: Session,
) -> GenerationJob:
    """Generate certificates and record each recipient's result."""

    job = db.get(GenerationJob, job_id)

    if job is None:
        raise ValueError(f"Generation job {job_id} not found")

    job.status = "PROCESSING"
    db.commit()

    for recipient in job.recipients:
        recipient.status = "PROCESSING"
        db.commit()

        try:
            output_path = (
                OUTPUT_DIR
                / f"job_{job.id}"
                / f"certificate_{recipient.id}.pdf"
            )

            generate_certificate(
                recipient_name=recipient.name,
                certificate_title=job.certificate_title,
                organization=job.organization,
                output_path=output_path,
            )

            recipient.file_path = str(output_path)
            recipient.status = "SUCCESS"
            recipient.error_message = None

        except Exception:
            # Record this recipient's failure and continue
            # processing the remaining recipients.
            recipient.status = "FAILED"
            recipient.file_path = None
            recipient.error_message = (
                "Certificate generation failed. "
                "Check the application logs."
            )

        db.commit()

    # Recalculate totals from the actual recipient records.
    db.refresh(job)

    job.successful_count = sum(
        1 for recipient in job.recipients
        if recipient.status == "SUCCESS"
    )
    job.failed_count = sum(
        1 for recipient in job.recipients
        if recipient.status == "FAILED"
    )

    if job.failed_count == 0:
        job.status = "COMPLETED"
    elif job.successful_count == 0:
        job.status = "FAILED"
    else:
        job.status = "PARTIAL"

    db.commit()
    db.refresh(job)

    return job
