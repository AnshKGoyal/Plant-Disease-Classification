from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

'''
# SQLAlchemy ORM and Lazy Loading Quick Reference

1. Automatic Relationships:
   - SQLAlchemy ORM uses defined relationships to handle table connections
   - No need for explicit SQL joins to access related data

2. Lazy Loading:
   - Default behavior: related data fetched only when accessed
   - Automatic SQL generation and execution when accessing relationship attributes

3. No Explicit Queries Needed:
   - Simple operations don't require writing SQL
   - Python code and object relationships translated to SQL by SQLAlchemy

4. Automatic Condition Handling:
   - Foreign key relationships and conditions managed based on model setup

Example:
```python
# Fetch related user data automatically
comment = db.query(models.Comment).first()
user = comment.user  # SQLAlchemy generates and executes SQL behind the scenes
```

Benefits:
- Simplicity: Work with Python objects instead of SQL
- Maintainability: Model updates often sufficient for schema changes
- Performance: SQLAlchemy can optimize queries (e.g., batch loading)
- Flexibility: Easy switching between lazy loading, joined loading, etc.

Potential Pitfalls:
- N+1 Problem: Risk of many separate queries in loops
- Over-fetching: Automatic queries might retrieve more data than needed

Remember: Monitor query performance and use explicit joining or eager loading for optimization when necessary.
'''


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))

    images = relationship("Image", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")
    uploaded_images = relationship("Image", secondary="image_uploads", back_populates="uploaders")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    content_type = Column(String(50))
    uploaded_at = Column(DateTime, default=datetime.datetime.now)
    hash = Column(String(64), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="images")
    predictions = relationship("Prediction", back_populates="image")
    comments = relationship("Comment", back_populates="image")
    uploaders = relationship("User", secondary="image_uploads", back_populates="uploaded_images")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    disease = Column(String(100))
    confidence = Column(Float)
    predicted_at = Column(DateTime, default=datetime.datetime.now)

    image = relationship("Image", back_populates="predictions")
    user = relationship("User", back_populates="predictions")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_text = Column(String(1000))  # Adjust length as needed
    created_at = Column(DateTime, default=datetime.datetime.now)

    image = relationship("Image", back_populates="comments")
    user = relationship("User", back_populates="comments")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50))  # 'login' or 'logout'
    timestamp = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="activity_logs")

class ImageUpload(Base):
    __tablename__ = "image_uploads"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.datetime.now)

    image = relationship("Image", overlaps="uploaders,uploaded_images")
    user = relationship("User",  overlaps="uploaders,uploaded_images")
