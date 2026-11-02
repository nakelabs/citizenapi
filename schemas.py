from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# ==========================================
# Authentication Schemas
# ==========================================

class UserAuth(BaseModel):
    username: str = Field(..., min_length=2, max_length=100, description="Unique username")
    password: str = Field(..., min_length=3, max_length=100, description="User password")


class AuthResponse(BaseModel):
    token: str
    username: str
    id: int


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    reports_count: int


# ==========================================
# Incident Schemas
# ==========================================

class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Incident title or summary")
    category: str = Field(..., min_length=2, max_length=50, description="Category (Accident, Fighting, Rioting, Robbery, Other)")
    description: str = Field(..., min_length=3, description="Detailed description of the incident")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="GPS Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="GPS Longitude coordinate")
    photo_base64: Optional[str] = Field(None, description="Base64 encoded photo or data URI")


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    description: str
    latitude: float
    longitude: float
    photo_base64: Optional[str] = None
    created_at: datetime
    author_username: Optional[str] = "Anonymous"

