
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import Base, engine, get_db
from app.models import GenerationJob, Recipient
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
        certificate_title=request.certificate_title,
        organization=request.organization,
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
