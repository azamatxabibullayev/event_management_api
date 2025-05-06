from pydantic import BaseModel
from datetime import date


class EventBase(BaseModel):
    title: str
    description: str
    date: date
    location: str


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: date | None = None
    location: str | None = None


class EventOut(EventBase):
    id: int
    created_by_id: int

    class Config:
        orm_mode = True
