from sqlalchemy import(
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
    TIMESTAMP,
)

from .meta import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(Text, nullable=False)
    content = Column(Text)
    read = Column(Boolean(name="ck_message_read"), nullable=False, default=False)
    sent = Column(TIMESTAMP)

    def __json__(self, request):
        if self.message_type == 'text':
            return {
                'type': "text",
                'content': self.content,
                'sent': self.sent,
            }
