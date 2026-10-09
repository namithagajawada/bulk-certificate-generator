
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def current_time():
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    certificate_title: Mapped[str] = mapped_column(String(200))
    organization: Mapped[str] = mapped_column(String(200))

    status: Mapped[str] = mapped_column(
        String(30), default="PENDING"
    )
    total_recipients: Mapped[int] = mapped_column(Integer)
    successful_count: Mapped[int] = mapped_column(
        Integer, default=0
    )
    failed_count: Mapped[int] = mapped_column(
        Integer, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=current_time
    )

    recipients: Mapped[list["Recipient"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Recipient(Base):
    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("generation_jobs.id"), index=True
    )

    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30), default="PENDING"
    )
    file_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    job: Mapped["GenerationJob"] = relationship(
        back_populates="recipients"
    )
