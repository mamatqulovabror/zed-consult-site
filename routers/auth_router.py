from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, User
from auth import hash_password, verify_password, create_token, get_user_from_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterBody(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    password: str

class LoginBody(BaseModel):
    login: str
    password: str

@router.post("/register")
def register(body: RegisterBody, response: Response, db: Session = Depends(get_db)):
    if not body.email and not body.phone:
        raise HTTPException(400, "Email yoki telefon kerak")
    existing = None
    if body.email:
        existing = db.query(User).filter(User.email == body.email).first()
    if body.phone and not existing:
        existing = db.query(User).filter(User.phone == body.phone).first()
    if existing:
        raise HTTPException(400, "Bu foydalanuvchi allaqachon royxatdan otgan")
    user = User(email=body.email, phone=body.phone, full_name=body.full_name,
                hashed_password=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    token = create_token({"sub": str(user.id)})
    response.set_cookie("token", token, max_age=30*24*3600, httponly=True, samesite="lax")
    return {"ok": True, "user": {"id": user.id, "full_name": user.full_name}}

@router.post("/login")
def login(body: LoginBody, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == body.login) | (User.phone == body.login)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Login yoki parol notogri")
    token = create_token({"sub": str(user.id)})
    response.set_cookie("token", token, max_age=30*24*3600, httponly=True, samesite="lax")
    return {"ok": True, "user": {"id": user.id, "full_name": user.full_name}}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"ok": True}

@router.get("/me")
def me(token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    if not user:
        return {"user": None}
    return {"user": {"id": user.id, "full_name": user.full_name, "email": user.email,
                     "phone": user.phone, "is_admin": user.is_admin}}