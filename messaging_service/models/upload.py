"""
This model is intended to handle large uploads.
"""

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    total_size = Column(Integer, nullable=False)
    uploaded_size = Column(Integer, nullable=False, default=0)
    complete = Column(
        Boolean(name="ck_upload_complete"),
        nullable=False,
        default=False,
    )
    #available_on_s3 = Column(
    #    Boolean(name="ck_available_on_s3"),
    #    nullable=False,
    #    default=False,
    #)

    message = relationship(
        "Message",
        backref="upload",
        foreign_keys="Upload.message_id"
    )
