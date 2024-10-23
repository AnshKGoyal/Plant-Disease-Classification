import streamlit as st
import requests
import io
from PIL import Image

# FastAPI backend URL
API_URL = "http://localhost:8000"  # Update this if your FastAPI app is running on a different port

# Helper functions for API calls
def register_user(username, email, password):
    response = requests.post(
        f"{API_URL}/register",
        json={"username": username, "email": email, "password": password}
    )
    return response.json()

def login_user(username, password):
    response = requests.post(
        f"{API_URL}/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()
    else:
        #st.error("Login failed. Please check your credentials.")
        return None

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        result = login_user(username, password)
        if result and "token" in result:
            st.session_state['token'] = result['token']
            st.session_state['user'] = result['user']
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Login failed. Please check your credentials.")
    
    if st.button("Don't have an account? Register"):
        st.session_state['page'] = 'register'
        st.rerun()



def upload_image(file, token):
    img_byte_arr = io.BytesIO()
    image = Image.open(file)
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()

    files = {"file": (file.name, img_byte_arr, file.type)}
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_URL}/upload", files=files, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error during image upload: {str(e)}")
        return None

def predict_disease(image_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_URL}/predict", json={"image_id": image_id}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error during prediction request: {str(e)}")
        return None




def register_page():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    
    if st.button("Register"):
        result = register_user(username, email, password)
        if "id" in result:
            st.success("Registration successful! You can now log in.")
            st.session_state['page'] = 'login'
            st.rerun()
        else:
            st.error("Registration failed. Please try again.")
    
    if st.button("Already have an account? Login"):
        st.session_state['page'] = 'login'
        st.rerun()



def get_user_details(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users/{user_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user details.")
        return None

def get_images(token, skip=0, limit=100):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/images?skip={skip}&limit={limit}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch images.")
        return None

def get_image_details(image_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/images/{image_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch image details.")
        return None

def get_activity_logs(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/activity-logs", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch activity logs.")
        return None

def get_user_activity(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user/{user_id}/activity", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user activity.")
        return None

def post_comment(image_id, user_id, comment_text, token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "image_id": image_id,
        "user_id": user_id,
        "comment_text": comment_text
    }
    response = requests.post(f"{API_URL}/comment", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to post comment.")
        return None

def get_comments(image_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/comments/{image_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch comments.")
        return None


def get_all_predictions(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/all-predictions", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch predictions.")
        return None

def get_image_details(image_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/image-details/{image_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch image details.")
        return None
    

def logout():
    if 'token' in st.session_state:
        try:
            response = requests.post(f'{API_URL}/logout', params={'token': st.session_state.token})
            
            st.write(f"Response status code: {response.status_code}")
            st.write(f"Response content: {response.text}")
            
            if response.status_code == 200:
                st.session_state.clear()
                st.success("Logged out successfully")
                st.rerun()
            else:
                st.error(f"Failed to log out: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("No active session found.")
   



def main_page():
    st.title("Plant Disease Detection")
    st.write(f"Welcome, {st.session_state['user']['username']}!")
    
    menu = ["Upload Image", "My Images", "All Predictions", "Activity Logs", "User Profile"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "All Predictions":
        st.subheader("All Predicted Images")
        try:
            predictions = get_all_predictions(st.session_state['token'])
            if not predictions:
                st.warning("No predictions found")
                return

            # Pagination
            items_per_page = 9
            total_pages = (len(predictions) - 1) // items_per_page + 1
            page = st.selectbox("Page", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_predictions = predictions[start_idx:end_idx]

            col1, col2, col3 = st.columns(3)
            for idx, pred in enumerate(page_predictions):
                with col1 if idx % 3 == 0 else col2 if idx % 3 == 1 else col3:
                    image_url = f"{API_URL}/image/{pred['filename']}"
                    st.image(image_url, caption=f"Image {pred['id']}", use_column_width=True)
                    if st.button(f"View Details {pred['id']}"):
                        st.session_state['selected_image'] = pred['id']
                        st.rerun()

            st.write(f"Page {page} of {total_pages}")

        except Exception as e:
            st.error(f"Failed to fetch predictions: {str(e)}")
            return

        if 'selected_image' in st.session_state:
            try:
                details = get_image_details(st.session_state['selected_image'], st.session_state['token'])
                if details:
                    st.subheader(f"Details for Image {details['id']}")
                    st.image(f"{API_URL}/image/{details['filename']}", use_column_width=True)
                    st.write(f"Uploaded at: {details['uploaded_at']}")
                    if details['prediction']:
                        st.write(f"Prediction: {details['prediction']['disease']}")
                        st.write(f"Confidence: {details['prediction']['confidence']:.2f}")
                        st.write(f"Predicted at: {details['prediction']['predicted_at']}")

                    st.subheader("Comments")
                    for comment in details['comments']:
                        if comment.get('user') and comment['user'].get('username'):
                            st.text(f"{comment['user']['username']}: {comment['comment_text']}")
                        else:
                            st.text(f"Unknown user: {comment['comment_text']}")

                    new_comment = st.text_input("Add a comment:")
                    if st.button("Post Comment"):
                        if post_comment(details['id'], st.session_state['user']['id'], new_comment, st.session_state['token']):
                            st.success("Comment posted successfully!")
                            st.rerun()
                else:
                    st.warning("No details found for the selected image")

            except Exception as e:
                st.error(f"Failed to fetch image details: {str(e)}")
    
    elif choice == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image.', use_column_width=True)
            st.write("Analyzing image...")
            
            upload_result = upload_image(uploaded_file, st.session_state['token'])
            if upload_result and 'image' in upload_result and 'id' in upload_result['image']:
                image_id = upload_result['image']['id']
                
                prediction = predict_disease(image_id, st.session_state['token'])
                if prediction and 'disease' in prediction and 'confidence' in prediction:
                    st.success(f"Prediction: {prediction['disease']}")
                    st.success(f"Confidence: {prediction['confidence']:.2f}")
                    
                    # Add comment section
                    comment = st.text_area("Add a comment about this prediction:")
                    if st.button("Post Comment"):
                        if post_comment(image_id, st.session_state['user']['id'], comment, st.session_state['token']):
                            st.success("Comment posted successfully!")
                    
                    # Display comments
                    comments = get_comments(image_id, st.session_state['token'])
                    if comments:
                        st.subheader("Comments:")
                        for comment in comments:
                            st.text(f"{comment['user']['username']}: {comment['comment_text']}")
                else:
                    st.error("Failed to get a prediction. Please try again.")
            else:
                st.error("Failed to upload image. Please try again.")
    
    elif choice == "My Images":
        images = get_images(st.session_state['token'])
        if images:
            for image in images:
                st.subheader(f"Image ID: {image['id']}")
                st.write(f"Uploaded at: {image['uploaded_at']}")
                image_url = f"{API_URL}/image/{image['filename']}"
                st.image(image_url, caption=f"Image {image['id']}", use_column_width=True)
        else:
            st.write("No images found.")
    elif choice == "Activity Logs":
        logs = get_activity_logs(st.session_state['token'])
        if logs:
            for log in logs:
                st.write(f"User: {log['user']['username']}, Activity: {log['activity_type']}, Time: {log['timestamp']}")
    
    elif choice == "User Profile":
        user_details = get_user_details(st.session_state['user']['id'], st.session_state['token'])
        if user_details:
            st.subheader("User Profile")
            st.write(f"Username: {user_details['username']}")
            st.write(f"Email: {user_details['email']}")
            
            st.subheader("User Activity")
            user_activity = get_user_activity(st.session_state['user']['id'], st.session_state['token'])
            if user_activity:
                for activity in user_activity:
                    st.write(f"Activity: {activity['activity_type']}, Time: {activity['timestamp']}")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        logout()



# Main app logic
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    
    if 'token' not in st.session_state:
        if st.session_state['page'] == 'login':
            login_page()
        elif st.session_state['page'] == 'register':
            register_page()
    else:
        main_page()

if __name__ == "__main__":
    main()
