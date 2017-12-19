"""
This model is intended to handle large uploads.
"""
import os.path
import shutil

import boto3
from pyramid.settings import asbool
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
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

    def permanent_filename(self, request):
        return "{env_prefix}-message-{message_id}-{message_type}".format(
            env_prefix=request.registry.settings['instance_prefix'],
            message_id=self.message.id,
            message_type=self.message.message_type,
        )

    def link(self, request):
        if not self.complete:
            return None
        elif not self.available_on_s3:
            return request.static_url(
                "messaging_service:static/uploads/{}".format(
                    self.permanent_filename(request)
                )
            )

        s3 = boto3.client(
            's3',
            region_name=request.registry.settings.get('uploads.s3.region'),
        )

        return s3.generate_presigned_url(
            'get_object',
            Params=self.s3_location(request),
        )

    def s3_location(self, request):
        bucket_name = "{environment_prefix}.{bucket_name}".format(
            environment_prefix=request.registry.settings['environment_prefix'],
            bucket_name=request.registry.settings['uploads.s3.bucket'],
        )

        return {
            'Bucket': bucket_name,
            'Key': self.permanent_filename(request),
        }

    def copy_to_permanent_location(self, request):
        settings = request.registry.settings

        if asbool(settings.get('uploads.s3.enabled')):
            return self._upload_to_s3(request)

        permanent_filename = os.path.join(
            settings['uploads.permanent_directory'],
            self.permanent_filename(request),
        )

        with open(self.partial_filename(request), 'rb') as temporary_file:
            with open(permanent_filename, 'wb') as permanent_file:
                shutil.copyfileobj(temporary_file, permanent_file)

    def _upload_to_s3(self, request):
        s3 = boto3.resource('s3')
        s3_location = self.s3_location(request)

        with open(self.partial_filename(request), 'rb') as data:
            s3.Bucket(s3_location['Bucket']).put_object(
                Key=s3_location['Key'],
                Body=data,
            )

        self.available_on_s3 = True
        request.dbsession.add(self)
