from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String, index=True)
    destination_ip = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    bytes_sent = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)