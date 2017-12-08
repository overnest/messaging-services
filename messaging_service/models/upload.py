"""
This model is intended to handle large uploads.
"""
import os.path
import shutil

import boto3
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
    available_on_s3 = Column(
        Boolean(name="ck_available_on_s3"),
        nullable=False,
        default=False,
    )

    message = relationship("Message", back_populates="upload")

    def partial_filename(self, request):
        return os.path.join(
            request.registry.settings['uploads.temporary_directory'],
            "partial-upload.{upload_id}".format(upload_id=self.id),
        )

    def permanent_filename(self):
        return "message-{message_id}-{message_type}".format(
            message_id=self.message.id,
            message_type=self.message.message_type,
        )

    def link(self, request):
        if not self.complete:
            return None

        permanent_path = os.path.join(
            request.registry.settings['uploads.permanent_directory'],
            self.permanent_filename(),
        )

        return request.static_url("messaging_service:static/uploads/{}".format(self.permanent_filename()))

    def copy_to_permanent_location(self, request):
        settings = request.registry.settings

        # TODO: Integrate with S3
        if settings.get('uploads.s3.enabled'):
            return self._upload_to_s3(request)

        permanent_filename = os.path.join(
            settings['uploads.permanent_directory'],
            self.permanent_filename(),
        )

        with open(self.partial_filename(request), 'rb') as temporary_file:
            with open(permanent_filename, 'wb') as permanent_file:
                shutil.copyfileobj(temporary_file, permanent_file)

    def _upload_to_s3(self, request):
        bucket = request.registry.settings['uploads.s3.bucket']
        s3 = boto3.resource('s3')

        with open(self.partial_filename(request), 'rb') as data:
            s3.Bucket(bucket).put_object(Key=self.permanent_filename, Body=data)
