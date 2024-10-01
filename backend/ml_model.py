import numpy as np
import tensorflow as tf
from tensorflow import keras
from joblib import load
import os
from PIL import Image

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the parent directory
parent_dir = os.path.dirname(current_dir)

# Construct the path to the model file
MODEL_PATH = os.path.join(parent_dir, 'model', 'NasNetMobile.keras')
LABEL_ENCODER_PATH = os.path.join(parent_dir, 'model', 'label_encoder.joblib')

# Check if the model file exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Load the model and label encoder
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
label_encoder = load(LABEL_ENCODER_PATH)

TARGET_SIZE = (256, 256) 

def preprocess_image(image_path, target_size=TARGET_SIZE):
    def _preprocess(image_path_tensor):
        image_path = image_path_tensor.numpy().decode('utf-8')
        with tf.io.gfile.GFile(image_path, 'rb') as file:
            img = Image.open(file).convert("RGB")
        img = np.array(img)
        return img

    img = tf.py_function(_preprocess, [image_path], tf.uint8)
    img.set_shape((None, None, 3))
    
    img = tf.image.resize_with_pad(
        img, 
        target_size[0], 
        target_size[1], 
        method=tf.image.ResizeMethod.BILINEAR
    )
    img = tf.cast(img, tf.float32) / 255.
    return img
    

def predict_disease(image_path):
    # Preprocess the image
    img = preprocess_image(image_path)
    img = tf.expand_dims(img, axis=0)  # Add batch dimension
    
    # Make prediction
    prediction = model.predict(img)
    
    # Get the predicted class index
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    
    # Get the predicted class name
    predicted_class = label_encoder.inverse_transform([predicted_class_index])[0]
    
    # Get the confidence
    confidence = np.max(prediction)
    
    return predicted_class, float(confidence)