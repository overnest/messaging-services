from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    from_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_type = Column(Text, nullable=False)
    content = Column(Text)
    read = Column(Boolean(name="ck_message_read"), nullable=False, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    upload = relationship("Upload", uselist=False, back_populates="message")

    def __json__(self, request):
        if self.message_type == 'text':
            return {
                'type': "text",
                'content': self.content,
                'timestamp': self.timestamp.isoformat(),
                'from': self.from_user.username,
            }
        elif self.message_type == 'video':
            return {
                'type': "video",
                'contentLink': self.upload.link(request),
                'timestamp': self.timestamp.isoformat(),
                'from': self.from_user.username,
            }
