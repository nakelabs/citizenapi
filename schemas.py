from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class UserAuth(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=3, max_length=100)


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


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    category: str = Field(..., min_length=2, max_length=50)
    description: str = Field(..., min_length=3)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    photo_base64: Optional[str] = None


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
