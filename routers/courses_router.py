from fastapi import APIRouter, HTTPException, Cookie
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends
from database import get_db, Course, Purchase
from auth import get_user_from_token
import os

BUNNY_LIB_ID = os.getenv("BUNNY_LIB_ID", "621629")
router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("/")
def get_courses(section: str = None, db: Session = Depends(get_db)):
    q = db.query(Course).filter(Course.is_active == True)
    if section:
        q = q.filter(Course.section == section)
    return [{"id": c.id, "section": c.section, "country": c.country, "degree": c.degree,
             "title": c.title, "price": c.price} for c in q.all()]

@router.get("/{course_id}/watch")
def watch(course_id: int, token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if not user:
        raise HTTPException(401, "Login kerak")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, "Kurs topilmadi")
    if not user.is_admin:
        p = db.query(Purchase).filter(Purchase.user_id == user.id,
            Purchase.course_id == course_id, Purchase.status == "paid").first()
        if not p:
            raise HTTPException(403, "Sotib oling")
    if not course.bunny_video_id:
        raise HTTPException(404, "Video yuklanmagan")
    embed = f"https://iframe.mediadelivery.net/embed/{BUNNY_LIB_ID}/{course.bunny_video_id}?autoplay=false&responsive=true"
    return {"embed_url": embed, "title": course.title}

class CourseBody(BaseModel):
    section: str
    country: str
    degree: Optional[str] = None
    title: str
    description: Optional[str] = None
    price: float = 45.0
    bunny_video_id: Optional[str] = None

@router.post("/")
def create(body: CourseBody, token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin kerak")
    c = Course(**body.dict()); db.add(c); db.commit(); db.refresh(c)
    return {"ok": True, "id": c.id}

@router.put("/{course_id}")
def update(course_id: int, body: CourseBody, token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin kerak")
    c = db.query(Course).filter(Course.id == course_id).first()
    if not c:
        raise HTTPException(404, "Topilmadi")
    for k, v in body.dict().items():
        setattr(c, k, v)
    db.commit()
    return {"ok": True}