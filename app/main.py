
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import Base, engine, get_db
from app.models import GenerationJob, Recipient
from app.services.job_service import process_generation_job

from pathlib import Path

from fastapi.responses import FileResponse, Response

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile



from app.schemas import (
    CreateJobRequest,
    JobResponse,
    JobStatusResponse,
    RecipientStatusResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Generate and track certificates in bulk.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Bulk Certificate Generator API is running"}



@app.post(
    "/api/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    request: CreateJobRequest,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        certificate_title=request.certificate_title.strip(),
        organization=request.organization.strip(),
        total_recipients=len(request.recipients),
        status="PENDING",
    )

    for item in request.recipients:
        job.recipients.append(
            Recipient(
                name=item.name.strip(),
                email=item.email,
                status="PENDING",
            )
        )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Process every recipient and update the database.
    job = process_generation_job(job.id, db)

    return JobResponse(
        job_id=job.id,
        status=job.status,
        total_recipients=job.total_recipients,
        successful_count=job.successful_count,
        failed_count=job.failed_count,
    )


@app.get(
    "/api/jobs/{job_id}",
    response_model=JobStatusResponse,
)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(GenerationJob, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        total_recipients=job.total_recipients,
        successful_count=job.successful_count,
        failed_count=job.failed_count,
        recipients=[
            RecipientStatusResponse(
                recipient_id=recipient.id,
                name=recipient.name,
                status=recipient.status,
                error_message=recipient.error_message,
            )
            for recipient in job.recipients
        ],
    )

@app.get("/api/recipients/{recipient_id}/certificate")
def download_certificate(
    recipient_id: int,
    db: Session = Depends(get_db),
):
    recipient = db.get(Recipient, recipient_id)

    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found",
        )

    if recipient.status != "SUCCESS" or not recipient.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate is not available",
        )

    file_path = Path(recipient.file_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"certificate_{recipient.id}.pdf",
    )


@app.get("/api/jobs/{job_id}/certificates.zip")
def download_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(GenerationJob, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    buffer = BytesIO()
    added_count = 0

    with ZipFile(
        buffer,
        mode="w",
        compression=ZIP_DEFLATED,
    ) as archive:
        for recipient in job.recipients:
            if recipient.status != "SUCCESS" or not recipient.file_path:
                continue

            file_path = Path(recipient.file_path)

            if not file_path.is_file():
                continue

            archive.write(
                file_path,
                arcname=f"certificate_{recipient.id}.pdf",
            )
            added_count += 1

    if added_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No generated certificates are available",
        )

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                f'attachment; filename="job_{job.id}_certificates.zip"'
            )
        },
    )
