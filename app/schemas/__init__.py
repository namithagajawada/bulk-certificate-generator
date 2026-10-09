
from pydantic import BaseModel, Field, field_validator


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Recipient name cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        if not value:
            return None

        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Please provide a valid email address")

        return value


class CreateJobRequest(BaseModel):
    certificate_title: str = Field(min_length=1, max_length=200)
    organization: str = Field(min_length=1, max_length=200)
    recipients: list[RecipientInput] = Field(min_length=1)

    @field_validator("certificate_title", "organization")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value


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
