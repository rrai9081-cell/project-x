import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from typing import List

from . import models, schemas, database
from .database import engine, get_db

# Create DB Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AyuConnect API", version="1.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Configurations
SECRET_KEY = "ayuconnect_secret_key_change_me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password Utilities
def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get Current User Dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email, role=payload.get("role"))
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ENDPOINTS ---

@app.post("/api/v1/auth/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role, 
        "user_id": user.id
    }

# --- ELDERS ENDPOINTS ---

@app.post("/api/v1/elders", response_model=schemas.ElderResponse)
def create_elder(elder: schemas.ElderCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_elder = models.Elder(
        sponsor_id=current_user.id,
        name=elder.name,
        dob=elder.dob,
        address=elder.address,
        medical_history=elder.medical_history,
        wearable_device_id=elder.wearable_device_id
    )
    db.add(new_elder)
    db.commit()
    db.refresh(new_elder)
    return new_elder

@app.get("/api/v1/elders", response_model=List[schemas.ElderResponse])
def get_my_elders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "ADMIN":
        return db.query(models.Elder).all()
    return db.query(models.Elder).filter(models.Elder.sponsor_id == current_user.id).all()

# --- VITALS ENDPOINTS ---

@app.post("/api/v1/elders/{elder_id}/vitals", response_model=schemas.VitalsLogResponse)
def log_vitals(elder_id: str, vitals: schemas.VitalsLogCreate, db: Session = Depends(get_db)):
    elder = db.query(models.Elder).filter(models.Elder.id == elder_id).first()
    if not elder:
        raise HTTPException(status_code=404, detail="Elder not found")
    
    new_log = models.VitalsLog(
        elder_id=elder_id,
        heart_rate=vitals.heart_rate,
        spo2=vitals.spo2,
        activity_level=vitals.activity_level
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.get("/api/v1/elders/{elder_id}/vitals", response_model=List[schemas.VitalsLogResponse])
def get_vitals(elder_id: str, db: Session = Depends(get_db)):
    return db.query(models.VitalsLog).filter(models.VitalsLog.elder_id == elder_id).order_by(models.VitalsLog.time.desc()).limit(50).all()

# --- SERVICE REQUESTS ENDPOINTS ---

@app.post("/api/v1/requests", response_model=schemas.ServiceRequestResponse)
def create_service_request(request: schemas.ServiceRequestCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_req = models.ServiceRequest(
        elder_id=request.elder_id,
        type=request.type,
        notes=request.notes,
        status="PENDING"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

@app.get("/api/v1/requests", response_model=List[schemas.ServiceRequestResponse])
def get_service_requests(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "ADMIN":
        return db.query(models.ServiceRequest).all()
    # Find all requests for elders sponsored by current user
    elder_ids = [e.id for e in current_user.elders_sponsored]
    return db.query(models.ServiceRequest).filter(models.ServiceRequest.elder_id.in_(elder_ids)).all()

@app.put("/api/v1/requests/{request_id}/status", response_model=schemas.ServiceRequestResponse)
def update_request_status(request_id: str, status: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = status
    if current_user.role == "BUDDY" or current_user.role == "ADMIN":
        req.assigned_to = current_user.id
    db.commit()
    db.refresh(req)
    return req

# --- DATA SEEDING SETUP ---

@app.on_event("startup")
def seed_data():
    db = database.SessionLocal()
    try:
        # Create seed admin and sponsor if none exist
        admin = db.query(models.User).filter(models.User.email == "admin@ayuconnect.com").first()
        if not admin:
            hashed_pw = get_password_hash("admin123")
            admin_user = models.User(
                email="admin@ayuconnect.com",
                password_hash=hashed_pw,
                phone="9876543210",
                role="ADMIN"
            )
            db.add(admin_user)
            
            sponsor_pw = get_password_hash("sponsor123")
            sponsor_user = models.User(
                email="sponsor@ayuconnect.com",
                password_hash=sponsor_pw,
                phone="9988776655",
                role="SPONSOR"
            )
            db.add(sponsor_user)
            db.commit()
            
            # Seed elder for this sponsor
            db.refresh(sponsor_user)
            elder = models.Elder(
                sponsor_id=sponsor_user.id,
                name="Savitri Devi",
                dob="1952-08-15",
                address="45, Gated Paradise Enclave, Koramangala, Bangalore",
                medical_history="Hypertension, Mild Arthritis",
                wearable_device_id="fitbit_9921_x"
            )
            db.add(elder)
            db.commit()
            
            db.refresh(elder)
            # Seed mock vitals logs
            import random
            time_now = datetime.utcnow()
            for i in range(24):
                v_log = models.VitalsLog(
                    elder_id=elder.id,
                    heart_rate=random.randint(70, 95),
                    spo2=random.randint(95, 99),
                    activity_level=random.choice(["Active", "Resting", "Sleeping", "Sedentary"]),
                    time=time_now - timedelta(hours=i)
                )
                db.add(v_log)
                
            # Seed mock service requests
            req1 = models.ServiceRequest(
                elder_id=elder.id,
                type="MEDICAL",
                notes="Bi-weekly BP and Sugar screening test session setup.",
                status="RESOLVED"
            )
            req2 = models.ServiceRequest(
                elder_id=elder.id,
                type="GROCERY",
                notes="Refill for monthly diabetes and arthritis medicines.",
                status="PENDING"
            )
            db.add(req1)
            db.add(req2)
            db.commit()
            print("Successfully seeded mock data for development!")
    finally:
        db.close()

# --- ADMIN STATISTICS ENDPOINT ---

@app.get("/api/v1/admin/stats")
def get_admin_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to access admin metrics")
    
    total_sponsors = db.query(models.User).filter(models.User.role == "SPONSOR").count()
    total_elders = db.query(models.Elder).count()
    
    # Concierge stats
    pending_tickets = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "PENDING").count()
    in_prog_tickets = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "IN_PROGRESS").count()
    resolved_tickets = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "RESOLVED").count()
    
    # Calculate mock predictive anomalies
    vitals = db.query(models.VitalsLog).all()
    hr_anomalies = sum(1 for v in vitals if v.heart_rate and (v.heart_rate > 90 or v.heart_rate < 65))
    spo2_anomalies = sum(1 for v in vitals if v.spo2 and v.spo2 < 95)
    
    return {
        "total_sponsors": total_sponsors,
        "total_elders": total_elders,
        "concierge": {
            "pending": pending_tickets,
            "in_progress": in_prog_tickets,
            "resolved": resolved_tickets
        },
        "anomalies": {
            "heart_rate_alerts": hr_anomalies,
            "oxygen_alerts": spo2_anomalies,
            "fall_risks_detected": 1
        },
        "avg_response_time_minutes": 24,
        "client_satisfaction_score": 98.4
    }

# Mount Static Frontend
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
