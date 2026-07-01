from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from backend.database import create_db, get_session
from backend.models import User
from backend.schemas import UserCreate

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Format Changer")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.on_event("startup")
def on_startup():
    create_db()


def create_user_db(session: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user_db(session: Session, user_id: int, user_data: dict) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user_db(session: Session, user_id: int) -> None:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()


# API endpoints
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    return create_user_db(session, user.model_dump())


@app.get("/users")
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    delete_user_db(session, user_id)
    return {"ok": True}


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, session: Session = Depends(get_session)):
    return update_user_db(session, user_id, user.model_dump())


# HTML routes
@app.get("/", name="home")
def users_page(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse(request, "users.html", {"request": request, "users": users})


@app.get("/user/add/", name="add_user_page")
def add_user_page(request: Request):
    return templates.TemplateResponse(request, "add_user.html", {"request": request})


@app.post("/user/add/", name="create_user_page")
def create_user_page(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    session: Session = Depends(get_session),
):
    create_user_db(session, {"name": name, "email": email})
    return RedirectResponse(url=request.url_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/user/{user_id}", name="user_detail")
def user_detail_page(user_id: int, request: Request, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(request, "user_detail.html", {"request": request, "user": user})


@app.get("/user/edit/{user_id}", name="edit_user_page")
def edit_user_page(user_id: int, request: Request, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse(request, "edit_user.html", {"request": request, "user": user})


@app.post("/user/edit/{user_id}", name="update_user_page")
def update_user_page(
    user_id: int,
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    session: Session = Depends(get_session),
):
    update_user_db(session, user_id, {"name": name, "email": email})
    return RedirectResponse(url=request.url_for("user_detail", user_id=user_id), status_code=status.HTTP_303_SEE_OTHER)


@app.post("/user/delete/{user_id}", name="delete_user_page")
def delete_user_page(user_id: int, request: Request, session: Session = Depends(get_session)):
    delete_user_db(session, user_id)
    return RedirectResponse(url=request.url_for("home"), status_code=status.HTTP_303_SEE_OTHER)