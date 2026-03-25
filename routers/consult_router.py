from fastapi import APIRouter, HTTPException, Cookie, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Consultation
from auth import get_user_from_token

router = APIRouter(prefix="/api/consult", tags=["consult"])

SLOTS = ["09:00-09:30","09:30-10:00","10:00-10:30","10:30-11:00",
    "11:00-11:30","11:30-12:00","14:00-14:30","14:30-15:00",
    "15:00-15:30","15:30-16:00","16:00-16:30","16:30-17:00",
    "17:00-17:30","17:30-18:00","18:00-18:30","18:30-19:00",
    "19:00-19:30","19:30-20:00","20:00-20:30","20:30-21:00"]

@router.get("/slots")
def get_slots():
    return {"slots": SLOTS}

class ConsultBody(BaseModel):
    full_name: str
    phone: str
    date: str
    time_slot: str

@router.post("/book")
def book(body: ConsultBody, db: Session = Depends(get_db)):
    existing = db.query(Consultation).filter(
        Consultation.date == body.date,
        Consultation.time_slot == body.time_slot,
        Consultation.status != "cancelled"
    ).first()
    if existing:
        raise HTTPException(400, "Bu vaqt band")
    c = Consultation(**body.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"ok": True, "id": c.id}

@router.get("/all")
def get_all(token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin kerak")
    items = db.query(Consultation).all()
    return [{"id": c.id, "full_name": c.full_name, "phone": c.phone,
             "date": c.date, "time_slot": c.time_slot, "status": c.status} for c in items]
