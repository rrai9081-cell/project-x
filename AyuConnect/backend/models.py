from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
import datetime
import uuid
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, default="SPONSOR") # ADMIN, SPONSOR, BUDDY, ELDER
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    elders_sponsored = relationship("Elder", back_populates="sponsor")
    subscriptions = relationship("Subscription", back_populates="sponsor")

class Elder(Base):
    __tablename__ = "elders"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    sponsor_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    dob = Column(String, nullable=True)
    address = Column(String, nullable=True)
    medical_history = Column(String, nullable=True)
    wearable_device_id = Column(String, nullable=True)

    # Relationships
    sponsor = relationship("User", back_populates="elders_sponsored")
    vitals = relationship("VitalsLog", back_populates="elder")
    requests = relationship("ServiceRequest", back_populates="elder")

class VitalsLog(Base):
    __tablename__ = "vitals_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    elder_id = Column(String, ForeignKey("elders.id"))
    heart_rate = Column(Integer, nullable=True)
    spo2 = Column(Integer, nullable=True)
    activity_level = Column(String, default="Sedentary")
    time = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    elder = relationship("Elder", back_populates="vitals")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    elder_id = Column(String, ForeignKey("elders.id"))
    type = Column(String, nullable=False) # MEDICAL, REPAIR, GROCERY, COMPANIONSHIP
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, RESOLVED, CANCELLED
    notes = Column(String, nullable=True)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    elder = relationship("Elder", back_populates="requests")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    sponsor_id = Column(String, ForeignKey("users.id"))
    plan = Column(String, default="BASIC") # BASIC, PREMIUM
    status = Column(String, default="ACTIVE") # ACTIVE, CANCELLED, PAST_DUE
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    sponsor = relationship("User", back_populates="subscriptions")
