**Objective**: Develop a model to classify images of plant leaves into categories of healthy or various diseases. This application can be useful for agricultural purposes, enabling farmers to quickly diagnose and treat plant diseases.

The Plant Disease Classification project uses the [NasNetMobile](https://keras.io/api/applications/nasnet/) deep learning model to classify plant conditions into five categories: fungus, healthy, virus, pests , and bacteria . With a FastAPI backend, SQL Server database, and Streamlit frontend, it enables users to upload images and get quick, accurate disease predictions.
## Project Structure

```scss
plant_disease_classification/
├── backend/
│   ├── app.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── schemas.py
│   ├── ml_model.py
│   └── uploads/
├── model/
│   ├── label_encoder.joblib
│   ├── NasNetMobile.keras
├── example_images/
├── plant-disease-classification.ipynb
├── requirements.txt
└── README.md

```
## Backend (FastAPI)

### app.py (Frontend - Streamlit)

- **Purpose**: Provides a web-based interface using Streamlit for user interaction with the backend API. Users can register, log in, upload images, view disease predictions, and leave comments on predictions.
    
- **Key Features**:
    
    - **User Registration and Login**: Users can register or log in to access the system. Session management is handled using tokens received from the FastAPI backend.
    - **Image Upload and Prediction**: Users can upload images for plant disease detection, and the system will display the predicted disease and confidence score.
    - **Comments Section**: Users can add comments on image predictions and view comments from others.
    - **Activity Logs**: Users can view their activity history, such as image uploads, predictions, and logins.
    - **Image Display**: The app dynamically displays uploaded images, allowing users to view and interact with their image predictions.
- **Main Features of `app.py`**:
    
    1. **Login Page**:
        - Users can log in with their credentials. If they don't have an account, they can switch to the registration page.
    2. **Register Page**:
        - Users can register for an account by providing a username, email, and password.
    3. **Main Page**:
        - After logging in, users are greeted with a dashboard that includes several options:
            - **Upload Image**: Users can upload plant leaf images for disease prediction.
            - **My Images**: Users can view all the images they have uploaded.
            - **All Predictions**: Users can see a paginated list of all images with predictions made.
            - **Activity Logs**: Users can review their activity logs.
            - **User Profile**: View details about the logged-in user’s profile and their activity history.
    4. **Image Upload**:
        - Users can upload a JPG, JPEG, or PNG image file.
        - Once uploaded, the app interacts with the backend to save the image and provide a prediction.
        - The app displays the disease prediction and confidence score after processing.
        - Users can also leave comments on the predictions.
    5. **Comments on Predictions**:
        - After a prediction is made, users can add comments about the results. The comment is saved and displayed under the image.
    6. **Image Details**:
        - Users can view detailed information about each image, including its upload time, prediction result, and comments.
- **App Functionality**:
    
    - `register_user`, `login_user`, `upload_image`, `predict_disease`, `post_comment`, and more functions interact with the FastAPI backend to perform tasks such as registration, login, uploading images, making predictions, and retrieving data (images, predictions, comments, activity logs)
### main.py (Backend - FastAPI)

- **Purpose**: Handle API endpoints, integrate with the machine learning model, and manage database interactions.
    - **Endpoints**:
        - `/`: Root test endpoint.
        - `/register`: Endpoint to register a new user.
        - `/login`: Endpoint for user login.
        - `/upload`: Endpoint to upload images.
        - `/predict`: Endpoint to make predictions on uploaded images.
        - `/comments`: Endpoint to add and retrieve comments.
        - `/activity-logs`: Endpoint to retrieve user activity logs.
        - `/image-details/{image_id}`: Fetches the details of a specific image including predictions and comments.

### models.py

- **Purpose**: Defines the SQLAlchemy models for database structure.
- **Key Models**:
    - `User`: Stores user information.
    - `Image`: Represents the uploaded images, with metadata such as filename, content type, and hash.
    - `Prediction`: Stores the disease prediction results for each image.
    - `Comment`: Stores user comments associated with predictions.
    - `ActivityLog`: Tracks user activities like login and logout.
    - `ImageUpload`: Tracks instances of image uploads by users.

### database.py

- **Purpose**: Set up the database connection using SQLAlchemy and handle session management.
- **Key Components**:
    - `engine`: Configured for a local SQL Server.
    - `SessionLocal`: Manages database sessions.
    - `Base`: Base class for defining SQLAlchemy models.

### schemas.py

- **Purpose**: Define the Pydantic schemas for data validation and serialization in FastAPI.
- **Key Schemas**:
    - `UserCreate`, `UserLogin`, `User`: Handle user data.
    - `Image`, `UploadResponse`: Handle image data.
    - `Prediction`: Handles prediction results.
    - `CommentCreate`, `CommentWithUser`: Manage comments on images.
    - `ActivityLogWithUser`: Handles activity logs with user details.

## Machine Learning Model

### ml_model.py

- **Purpose**: Load the trained model and perform image classification using Keras and TensorFlow.
- **Model**: NasNetMobile architecture, pre-trained and fine-tuned for plant disease detection.
- **Label Encoder**: Maps the predicted class indices to disease names.
- **Prediction Process**:
    - The image is resized and preprocessed.
    - The model predicts the disease class and confidence score.
    - Results are returned to the user along with metadata.

### plant-disease-classification.ipynb

- **Purpose**: A Jupyter Notebook for training the model, performing data preprocessing, model evaluation, and optimization.
- **Key Components**:
    - Training on the NasNetMobile architecture.
    - Exporting the trained model and label encoder for deployment.

## Dataset
- **Download Links**:
    - [Plant pathogens dataset](https://www.kaggle.com/datasets/sujallimje/plant-pathogens) - licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Detailed Framework

### Database Schema

1. **users**
    
    - id (Primary Key)
    - username (Unique, Indexed)
    - email (Unique, Indexed)
    - password
2. **images**
    
    - id (Primary Key)
    - filename (Indexed)
    - content_type
    - uploaded_at
    - hash (Unique, Indexed)
    - user_id (Foreign Key to users.id)
3. **predictions**
    
    - id (Primary Key)
    - image_id (Foreign Key to images.id)
    - disease
    - confidence
    - predicted_at
4. **comments**
    
    - id (Primary Key)
    - image_id (Foreign Key to images.id)
    - user_id (Foreign Key to users.id)
    - comment_text
    - created_at
5. **activity_logs**
    
    - id (Primary Key)
    - user_id (Foreign Key to users.id)
    - activity_type
    - timestamp
6. **image_uploads**
    
    - id (Primary Key)
    - image_id (Foreign Key to images.id)
    - user_id (Foreign Key to users.id)
    - uploaded_at

### API Endpoints

1. **User Registration**:
    
    - **Endpoint**: `POST /register`
    - **Description**: Register a new user by providing `username`, `email`, and `password`.
    - **Response**: Returns the registered user details.
2. **User Login**:
    
    - **Endpoint**: `POST /login`
    - **Description**: Authenticate a user with `username` and `password`.
    - **Response**: Returns a token for authentication and user details.
3. **User Logout**:
    
    - **Endpoint**: `POST /logout`
    - **Description**: Logs out the user by invalidating their session token.
    - **Response**: Confirmation of logout.
4. **Upload Image**:
    
    - **Endpoint**: `POST /upload`
    - **Description**: Upload an image for disease prediction. The user must be authenticated via a token.
    - **Response**: Returns image details and upload record.
5. **Predict Disease**:
    
    - **Endpoint**: `POST /predict`
    - **Description**: Predict the disease based on an uploaded image's `image_id`. The user must be authenticated via a token.
    - **Response**: Returns the disease prediction and confidence level.
6. **Add Comment**:
    
    - **Endpoint**: `POST /comment`
    - **Description**: Add a comment to a specific image's prediction using `image_id` and `comment_text`.
    - **Response**: Returns the newly added comment with user details.
7. **Get Comments**:
    
    - **Endpoint**: `GET /comments/{image_id}`
    - **Description**: Fetch all comments associated with a particular image.
    - **Response**: Returns a list of comments with user details.
8. **Get Activity Logs**:
    
    - **Endpoint**: `GET /activity-logs`
    - **Description**: Retrieve logs of user activities such as login and logout.
    - **Response**: Returns a list of activity logs with user details.
9. **Get User Activity**:
    
    - **Endpoint**: `GET /user/{user_id}/activity`
    - **Description**: Fetch activity logs of a specific user based on `user_id`.
    - **Response**: Returns a list of activity logs for the specified user.
10. **List Uploaded Images**:
    
    - **Endpoint**: `GET /images`
    - **Description**: Fetch a list of images uploaded by the authenticated user. Can specify `skip` and `limit` for pagination.
    - **Response**: Returns a list of images uploaded by the user.
11. **Get Image Details**:
    
    - **Endpoint**: `GET /image-details/{image_id}`
    - **Description**: Get detailed information about an image, including its prediction and comments.
    - **Response**: Returns the image's details along with associated predictions and comments.
12. **Get All Predictions**:
    
    - **Endpoint**: `GET /all-predictions`
    - **Description**: Retrieve all images that have predictions associated with them.
    - **Response**: Returns a list of images and their associated prediction details.
13. **Serve Uploaded Image**:
    
    - **Endpoint**: `GET /image/{image_filename}`
    - **Description**: Serve the image file for display purposes based on its filename.
    - **Response**: Returns the image file.

## Detailed Planning

### Data Flow Diagram

![image](https://github.com/user-attachments/assets/d21c8a7e-70a8-4895-b342-f1f64c7dc63f)

### Entity Relationship Diagram

![new](https://github.com/user-attachments/assets/14b9553c-fac5-4e6a-b20c-740e45238d07)


- **PK** denotes primary key,
- **FK** denotes foreign key,
- **INT**, **VARCHAR**, and **DATETIME** denote data types.
- || indicates a mandatory 1-to-1 relationship.
- o{ indicates a zero-to-many relationship.
- { indicates a many-to-many relationship.
### Database Design

This database design efficiently manages users, images, comments, predictions, and activity logs. Here's a brief overview:

#### **Core Entities** 

-  **Users** : Stores user details _id as the primary key_.

-  **Images** : Tracks uploaded images, linked to users via user_id _foreign key_.

- **Comments** : Contains comments on images, linked by image_id and user_id _foreign keys_.

- **Predictions** : Stores image predictions with foreign keys linking to both users and images.

- **Activity Logs** : Logs user activities like logins/uploads, linked to users via user_id.

#### **Key Relationships** :

-  **Users to Images, Comments, Predictions, and Logs** : One user can create many entries one−to−many.

- **Images to Comments and Predictions** : One image can have many comments and predictions one−to−many.

####   **Integrity and Constraints** :

- **Primary Keys** : Ensure uniqueness of records in all tables.

- **Foreign Keys** : Ensure proper links between related tables for data consistency.

- **NOT NULL** : Prevents orphaned records _i_._e_.,_every commentor activity log must have an associated user_.

## Frontend Details (Streamlit)

- **User Authentication**: Provides pages for user registration and login. Authentication tokens are used to manage user sessions securely​.
- **Upload Image**: Users can upload images of plant leaves for disease prediction. The uploaded image is sent to the FastAPI backend, where predictions are made, and the results are displayed on the frontend​.
- **Prediction Display**: Displays the predicted disease class and the model’s confidence level for the uploaded images​.
- **Comments Section**: Users can leave comments on the predicted results and view comments from others​.
- **User Activity Logs**: Displays logs of user activities, such as login and logout events, and tracks which images they have uploaded​.
- **User Profile Page**: Displays user details and their associated activity logs​.

# References
1.	FastAPI documentation
2.	Streamlit documentation
3.	SQLAlchemy documentation
4.	TensorFlow and Keras documentation
5.	Plant Pathogens dataset on Kaggle
6.	Research papers related to NasNet and Resnet cnn architectures.
7.	SQL Server documentation
8.	Python Libraries (as per  requirements.txt)
9.	Additional relevant resources
10.	My personal Obsidian Notes


# Project Links:

- [github link](https://github.com/AnshKGoyal/Plant-Disease-Classification)
- [kaggle link](https://www.kaggle.com/code/anshkgoyal/plant-disease-classification)
