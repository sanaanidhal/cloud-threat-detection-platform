from pydantic import BaseModel
from datetime import datetime

class LogCreate(BaseModel):
    source_ip: str
    destination_ip: str
    port: int
    protocol: str
    bytes_sent: int
    timestamp: datetime

class LogResponse(LogCreate):
    id: int

    class Config:
        orm_mode = True