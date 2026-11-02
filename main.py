from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, SessionLocal, get_db
from models import User, Incident
from schemas import (
    UserAuth,
    AuthResponse,
    UserMeResponse,
    IncidentCreate,
    IncidentResponse,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_optional,
)

def seed_database():
    db = SessionLocal()
    try:
        if db.query(Incident).count() == 0:
            seed_user = db.query(User).filter(User.username == "LagosWatch").first()
            if not seed_user:
                seed_user = User(
                    username="LagosWatch",
                    password=hash_password("citizen2026pass")
                )
                db.add(seed_user)
                db.commit()
                db.refresh(seed_user)

            sample_incidents = [
                Incident(
                    title="Multi-vehicle collision along Lekki-Epe Expressway",
                    category="Accident",
                    description="Two commercial buses and a saloon car collided near Chisco Bus Stop heading towards Ajah. Emergency medical services (LASAMBUS) and traffic management operatives are on site.",
                    latitude=6.4414,
                    longitude=3.4988,
                    photo_base64=None,
                    author_id=seed_user.id
                ),
                Incident(
                    title="Civil disturbance and roadblock near Ojuelegba Underbridge",
                    category="Rioting",
                    description="Youth unrest with tires burning on the transit corridor disrupting vehicular movement along Western Avenue. Commuters are advised to divert via Surulere bypass.",
                    latitude=6.5142,
                    longitude=3.3619,
                    photo_base64=None,
                    author_id=seed_user.id
                ),
                Incident(
                    title="Violent clash between rival groups at Mile 12 Market",
                    category="Fighting",
                    description="Traders and transport union factions in physical confrontation around the market entrance. Police rapid response squad deployed to secure the perimeter.",
                    latitude=6.6118,
                    longitude=3.3986,
                    photo_base64=None,
                    author_id=seed_user.id
                ),
                Incident(
                    title="Armed robbery foiled along Otigba Street, Computer Village",
                    category="Robbery",
                    description="Suspected robbery attempt intercepted by local vigilantes and Ikeja police operatives. Perimeter is secure and shops are reopening.",
                    latitude=6.5937,
                    longitude=3.3364,
                    photo_base64=None,
                    author_id=seed_user.id
                )
            ]

            db.add_all(sample_incidents)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="Citizens Incident Reporting API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "Citizens Incident Reporting API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "incidents": "/incidents",
            "auth_login": "/auth/login",
            "auth_register": "/auth/register",
            "auth_me": "/auth/me"
        }
    }


@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(credentials: UserAuth, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == credentials.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    new_user = User(
        username=credentials.username,
        password=hash_password(credentials.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(user_id=new_user.id, username=new_user.username)
    return AuthResponse(token=token, username=new_user.username, id=new_user.id)


@app.post("/auth/login", response_model=AuthResponse, tags=["Auth"])
def login(credentials: UserAuth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        user = User(
            username=credentials.username,
            password=hash_password(credentials.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    token = create_access_token(user_id=user.id, username=user.username)
    return AuthResponse(token=token, username=user.username, id=user.id)


@app.get("/auth/me", response_model=UserMeResponse, tags=["Auth"])
def get_auth_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reports_count = db.query(Incident).filter(Incident.author_id == current_user.id).count()
    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at,
        reports_count=reports_count
    )


@app.get("/incidents", response_model=List[IncidentResponse], tags=["Incidents"])
def get_incidents(
    category: Optional[str] = Query("All"),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if category and category.strip().lower() != "all":
        query = query.filter(func.lower(Incident.category) == category.strip().lower())

    return query.order_by(Incident.created_at.desc()).all()


@app.get("/incidents/me", response_model=List[IncidentResponse], tags=["Incidents"])
def get_my_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Incident)
        .filter(Incident.author_id == current_user.id)
        .order_by(Incident.created_at.desc())
        .all()
    )


@app.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, tags=["Incidents"])
def create_incident(
    incident_data: IncidentCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    new_incident = Incident(
        title=incident_data.title,
        category=incident_data.category,
        description=incident_data.description,
        latitude=incident_data.latitude,
        longitude=incident_data.longitude,
        photo_base64=incident_data.photo_base64,
        author_id=current_user.id if current_user else None
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident
