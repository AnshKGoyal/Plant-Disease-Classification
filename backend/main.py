from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Header, Body
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import os
import shutil
import hashlib
from datetime import datetime, timedelta
import secrets
from typing import Dict
import models
import schemas
from database import SessionLocal, engine
from ml_model import predict_disease
from fastapi.responses import FileResponse
from sqlalchemy import or_,func,and_

os.makedirs("uploads", exist_ok=True)

app = FastAPI()
security = HTTPBearer()


@app.get("/")
async def read_root():
    """
    Root endpoint to test if the server is running.
    Returns a simple JSON response with a working message.
    """
    return {"App": "Working"}

# Create tables
models.Base.metadata.create_all(bind=engine)

# Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory store for sessions (not for production use)
user_sessions = {}
#FastAPI uses Depends() to declare dependencies. Dependencies are functions or objects that are provided automatically by the framework when needed in other parts of the code.
def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    user_id = user_sessions.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.LoginResponse)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Generate a session token
    token = secrets.token_hex(16)
    user_sessions[token] = db_user.id

    # Log the login activity
    activity_log = models.ActivityLog(user_id=db_user.id, activity_type="login")
    db.add(activity_log)
    db.commit()
    
    return {"token": token, "user": schemas.User.model_validate(db_user)}

@app.post("/logout")
def logout_user(token: str, db: Session = Depends(get_db)):
    if token in user_sessions:
        user_id = user_sessions.pop(token)
        # Log the logout activity
        activity_log = models.ActivityLog(user_id=user_id, activity_type="logout")
        db.add(activity_log)
        db.commit()
        return {"message": "Logged out successfully"}
    raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/upload", response_model=schemas.UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    user: models.User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    # Generate hash
    file_contents = await file.read()
    file_hash = hashlib.md5(file_contents).hexdigest()
    

    # Check if an image with this hash already exists
    existing_image = db.query(models.Image).filter(models.Image.hash == file_hash).first()
    if existing_image:
        upload_record = models.ImageUpload(image_id=existing_image.id, user_id=user.id)
        db.add(upload_record)
        db.commit()
        db.refresh(upload_record)
        return schemas.UploadResponse(image=existing_image, upload=upload_record)
    
    # If no existing image, proceed with upload
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(file_contents)
    
    # Create database entry
    db_image = models.Image(
        filename=unique_filename,
        content_type=file.content_type,
        hash=file_hash,
        user_id=user.id
    )
    db.add(db_image)
    try:
        db.commit()
        db.refresh(db_image)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error uploading image. Please try again.")
    
    # Create upload record
    upload_record = models.ImageUpload(image_id=db_image.id, user_id=user.id)
    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)
    
    return schemas.UploadResponse(image=db_image, upload=upload_record)

@app.post("/predict", response_model=schemas.Prediction)
async def predict(
    data: Dict[str, int] = Body(...),
    user: models.User = Depends(get_user_from_token),
    db: Session = Depends(get_db)
):
    image_id = data.get("image_id")
    if image_id is None:
        raise HTTPException(status_code=400, detail="image_id is required")

    db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Perform prediction
    image_path = os.path.join("uploads", db_image.filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        disease, confidence = predict_disease(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")
    
    # Create database entry
    db_prediction = models.Prediction(
        image_id=db_image.id,
        user_id=user.id,
        disease=disease,
        confidence=confidence
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


@app.post("/comment", response_model=schemas.CommentWithUser)
async def add_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    db_comment = models.Comment(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Fetch the associated user
    user = db.query(models.User).filter(models.User.id == db_comment.user_id).first()
    
    return schemas.CommentWithUser(
        id=db_comment.id,
        image_id=db_comment.image_id,
        user_id=db_comment.user_id,
        comment_text=db_comment.comment_text,
        created_at=db_comment.created_at,
        user=schemas.User(
            id=user.id,
            username=user.username,
            email=user.email
        ) if user else None
    )

@app.get("/comments/{image_id}", response_model=List[schemas.CommentWithUser])
async def get_comments(image_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.image_id == image_id).all()
    
    # Fetch user information for each comment
    comments_with_users = []
    for comment in comments:
        user = db.query(models.User).filter(models.User.id == comment.user_id).first()
        comments_with_users.append(schemas.CommentWithUser(
            id=comment.id,
            image_id=comment.image_id,
            user_id=comment.user_id,
            comment_text=comment.comment_text,
            created_at=comment.created_at,
            user=schemas.User(id=user.id, username=user.username, email=user.email)
        ))
    
    return comments_with_users





@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

'''@app.get("/images", response_model=List[schemas.Image])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(get_user_from_token)):
    # Query for images directly uploaded by the user or uploaded through image_uploads
    images = db.query(models.Image).filter(
        or_(
            models.Image.user_id == user.id,
            models.Image.uploaders.any(id=user.id)
        )
    ).order_by(models.Image.id).offset(skip).limit(limit).all()
    
    return [schemas.Image.model_validate(image) for image in images]'''

'''
@app.get("/images", response_model=List[schemas.UserImageUpload])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(get_user_from_token)):
    # Query for image uploads made by the user
    image_uploads = db.query(models.ImageUpload).filter(models.ImageUpload.user_id == user.id).\
        join(models.Image, models.ImageUpload.image_id == models.Image.id).\
        order_by(models.ImageUpload.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    return [schemas.UserImageUpload(
        id=upload.image.id,
        filename=upload.image.filename,
        content_type=upload.image.content_type,
        uploaded_at=upload.uploaded_at,
        user_id=upload.user_id
    ) for upload in image_uploads]'''

@app.get("/images", response_model=List[schemas.UserImageUpload])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: models.User = Depends(get_user_from_token)):
    # Subquery to get the latest upload for each image by the user
    latest_uploads = db.query(
        models.ImageUpload.image_id,
        func.max(models.ImageUpload.uploaded_at).label('latest_upload')
    ).filter(
        models.ImageUpload.user_id == user.id
    ).group_by(
        models.ImageUpload.image_id
    ).subquery()
    # Main query joining with the subquery to get only the latest upload for each image
    image_uploads = db.query(models.ImageUpload).join(
        latest_uploads,
        and_(
            models.ImageUpload.image_id == latest_uploads.c.image_id,
            models.ImageUpload.uploaded_at == latest_uploads.c.latest_upload
        )
    ).filter(
        models.ImageUpload.user_id == user.id
    ).join(
        models.Image, 
        models.ImageUpload.image_id == models.Image.id
    ).order_by(
        models.ImageUpload.uploaded_at.desc()
    ).offset(skip).limit(limit).all()
    return [schemas.UserImageUpload(
        id=upload.image.id,
        filename=upload.image.filename,
        content_type=upload.image.content_type,
        uploaded_at=upload.uploaded_at,
        user_id=upload.user_id
    ) for upload in image_uploads]

'''If a user uploads the same image multiple times:
There will be multiple entries in the image_uploads table.
The uploaders relationship will contain multiple entries for this user and image.
However, the .any() condition will still only return True once for this image.'''


# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/image/{image_filename}")
async def get_image(image_filename: str):
    image_path = f"uploads/{image_filename}"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Image not found")


@app.get("/activity-logs", response_model=List[schemas.ActivityLogWithUser])
async def get_activity_logs(db: Session = Depends(get_db)):
    logs = db.query(models.ActivityLog).all()
    
    # Fetch user information for each log
    logs_with_users = []
    for log in logs:
        user = db.query(models.User).filter(models.User.id == log.user_id).first()
        logs_with_users.append(schemas.ActivityLogWithUser(
            id=log.id,
            user_id=log.user_id,
            activity_type=log.activity_type,
            timestamp=log.timestamp,
            user=schemas.User(id=user.id, username=user.username, email=user.email)
        ))
    
    return logs_with_users

@app.get("/user/{user_id}/activity", response_model=List[schemas.ActivityLog])
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.ActivityLog).filter(models.ActivityLog.user_id == user_id).all()
    return [schemas.ActivityLog.model_validate(log) for log in logs]


@app.get("/all-predictions", response_model=List[schemas.ImageWithPrediction])
async def get_all_predictions(db: Session = Depends(get_db)):
    # Query all images that have predictions
    images_with_predictions = db.query(models.Image).join(models.Prediction).all()
    
    result = []
    for image in images_with_predictions:
        prediction = db.query(models.Prediction).filter(models.Prediction.image_id == image.id).first()
        result.append(schemas.ImageWithPrediction(
            id=image.id,
            filename=image.filename,
            uploaded_at=image.uploaded_at,
            prediction=schemas.Prediction(
                id=prediction.id,
                disease=prediction.disease,
                confidence=prediction.confidence,
                predicted_at=prediction.predicted_at,
                image_id=prediction.image_id,
                user_id=prediction.user_id
            )
        ))
    
    return result

@app.get("/image-details/{image_id}", response_model=schemas.ImageDetails)
async def get_image_details(image_id: int, db: Session = Depends(get_db)):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    prediction = db.query(models.Prediction).filter(models.Prediction.image_id == image_id).first()
    comments = db.query(models.Comment).filter(models.Comment.image_id == image_id).all()
    
    comments_with_user = []
    for comment in comments:
        user = db.query(models.User).filter(models.User.id == comment.user_id).first()
        comments_with_user.append(schemas.CommentWithUser(
            id=comment.id,
            image_id=comment.image_id,
            user_id=comment.user_id,
            comment_text=comment.comment_text,
            created_at=comment.created_at,
            user=schemas.User(
                id=user.id,
                username=user.username,
                email=user.email
            ) if user else None
        ))

    return schemas.ImageDetails(
        id=image.id,
        filename=image.filename,
        uploaded_at=image.uploaded_at,
        prediction=schemas.Prediction(
            id=prediction.id,
            disease=prediction.disease,
            confidence=prediction.confidence,
            predicted_at=prediction.predicted_at,
            image_id=prediction.image_id,
            user_id=prediction.user_id
        ) if prediction else None,
        comments=comments_with_user
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)