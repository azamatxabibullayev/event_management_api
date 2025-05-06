from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.models.event import Event
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(event_in: EventCreate, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    event = Event(**event_in.dict(), created_by_id=current_user.id)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/", response_model=list[EventOut])
async def list_events(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventOut)
async def update_event(event_id: int, event_in: EventUpdate, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update")
    for var, val in event_in.dict(exclude_none=True).items():
        setattr(event, var, val)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, current_user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete")
    await db.delete(event)
    await db.commit()
