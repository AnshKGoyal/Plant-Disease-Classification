from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class DiseaseClass(str, Enum):
    class1 = "bacteria"
    class2 = "fungus"
    class3 = "healthy"
    class4 = "pests"
    class5 = "virus"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
class UserLogin(BaseModel):
    username: str
    password: str
class User(UserBase):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True


class CommentWithUser(BaseModel):
    id: int
    image_id: int
    user_id: int
    comment_text: str
    created_at: datetime
    user: User

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    token: str
    user: User
class ImageBase(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=50)

class ImageCreate(ImageBase):
    hash: str = Field(..., max_length=64)
    user_id: int

class Image(ImageBase):
    id: int
    uploaded_at: datetime
    user_id: int
    hash: str
    uploaders: List[User] = []
    class Config:
        from_attributes = True


class ImageUpload(BaseModel):
    id: int
    image_id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    image: Image
    upload: ImageUpload

    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    disease: DiseaseClass
    confidence: float = Field(..., ge=0, le=1)

class PredictionCreate(PredictionBase):
    image_id: int
    user_id: int

class Prediction(BaseModel):
    id: int
    disease: DiseaseClass
    confidence: float
    predicted_at: datetime
    image_id: int
    user_id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    comment_text: str = Field(..., max_length=1000)

class CommentCreate(CommentBase):
    image_id: int
    user_id: int

class Comment(CommentBase):
    id: int
    created_at: datetime
    image_id: int
    user_id: int

    class Config:
        from_attributes = True


class ActivityLog(BaseModel):
    id: int
    user_id: int
    activity_type: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ActivityLogWithUser(BaseModel):
    id: int
    user_id: int
    activity_type: str
    timestamp: datetime
    user: User

    class Config:
        from_attributes = True

class ImageWithPrediction(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    prediction: Prediction

class ImageDetails(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    prediction: Optional[Prediction]
    comments: List[CommentWithUser]

    class Config:
        from_attributes = True

class UserImageUpload(BaseModel):
    id: int
    filename: str
    content_type: str
    uploaded_at: datetime
    user_id: int

    class Config:
        from_attributes = True