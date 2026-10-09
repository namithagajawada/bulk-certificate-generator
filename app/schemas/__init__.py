
from pydantic import BaseModel, Field


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: str | None = None


class CreateJobRequest(BaseModel):
    certificate_title: str = Field(
        min_length=1, max_length=200
    )
    organization: str = Field(
        min_length=1, max_length=200
    )
    recipients: list[RecipientInput] = Field(
        min_length=1
    )


class JobResponse(BaseModel):
    job_id: int
    status: str
    total_recipients: int
    successful_count: int
    failed_count: int


class RecipientStatusResponse(BaseModel):
    recipient_id: int
    name: str
    status: str
    error_message: str | None = None


class JobStatusResponse(JobResponse):
    recipients: list[RecipientStatusResponse]
