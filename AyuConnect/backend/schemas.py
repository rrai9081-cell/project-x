from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    role: Optional[str] = "SPONSOR"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Vitals Schemas
class VitalsLogBase(BaseModel):
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    activity_level: Optional[str] = "Sedentary"

class VitalsLogCreate(VitalsLogBase):
    pass

class VitalsLogResponse(VitalsLogBase):
    id: int
    elder_id: str
    time: datetime.datetime

    class Config:
        from_attributes = True

# Service Request Schemas
class ServiceRequestBase(BaseModel):
    type: str
    notes: Optional[str] = None

class ServiceRequestCreate(BaseModel):
    elder_id: str
    type: str
    notes: Optional[str] = None

class ServiceRequestResponse(ServiceRequestBase):
    id: str
    elder_id: str
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Elder Schemas
class ElderBase(BaseModel):
    name: str
    dob: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    wearable_device_id: Optional[str] = None

class ElderCreate(ElderBase):
    pass

class ElderResponse(ElderBase):
    id: str
    sponsor_id: str
    vitals: List[VitalsLogResponse] = []
    requests: List[ServiceRequestResponse] = []

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    plan: str
    status: str

class SubscriptionResponse(SubscriptionBase):
    id: str
    sponsor_id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
