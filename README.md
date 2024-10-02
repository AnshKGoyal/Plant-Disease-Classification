# Plant Disease Classification

This project is an automated system for plant disease classification using machine learning techniques. It aims to assist farmers, agricultural researchers, and enthusiasts in quickly and accurately diagnosing plant health issues through image analysis.

The application consists of a backend built with FastAPI, a database managed with SQL Server, and a frontend powered by Streamlit. The project leverages a pre-trained deep learning model to identify diseases from plant images.


## Features

- User registration and authentication
- Image upload and processing
- Automated disease classification using a deep learning model
- Community interaction through a comment system
- User activity logging
- Detailed prediction results with confidence scores

## Project Structure

```scss
plant_disease_classification/
├── backend/
│   ├── main.py                        # FastAPI main application
│   ├── models.py                      # SQLAlchemy models
│   ├── database.py                    # Database connection setup
│   ├── schemas.py                     # Pydantic schemas for data validation
│   ├── app.py                         # Streamlit frontend
│   ├── ml_model.py                    # Model loading and inference
│   └── uploads/                       # Directory to store uploaded images
├── model/			       
│   ├── label_encoder.joblib           # Label encoder for disease labels
│   ├── resnet_50_95.h5                # Pre-trained model
│   ├── NasNetMobile.h5                # Pre-trained model
│   ├── NasNetMobile.keras             # Pre-trained model
├── example_images/                    # Example images for testing
├── plant-disease-classification.ipynb # Jupyter notebook for training
├── requirements.txt                   # Dependencies for the project
└── README.md                          # Project documentation

```
**Note**: In case GitHub's LFS bandwidth limit is reached, you can also download the models using this [Google Drive link](https://drive.google.com/drive/folders/1sQCoF_Q6XmXKS3-YXhH8ZNv047P4L3By?usp=sharing).

## Demo Video

To see the Plant Disease Classification Web app in action, check out this demo video:


https://github.com/user-attachments/assets/4887ef70-9f47-4199-9f16-909a0df7fa41



## Installation

### Prerequisites

- [SQL Server 2022 Developer Edition](https://www.microsoft.com/en-in/sql-server/sql-server-downloads)
- [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16)
- Python 3.x


### Setup

1. Clone or Download the Repository and open the project directory in your editor (VS Code)

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows, use `.\venv\Scripts\activate`
```

3. Install the required dependencies:
```
python -m pip install -r requirements.txt
```
**Note**: If the bandwidth limit for GitHub LFS is exceeded and you cannot download the models, you can also use this [Google Drive link](https://drive.google.com/drive/folders/1sQCoF_Q6XmXKS3-YXhH8ZNv047P4L3By?usp=sharing) to download the models.

4. Update the `SERVER` and `DATABASE` variables in `backend/database.py` with your SQL Server details.
```
SERVER = 'your_server_name'
DATABASE = 'plant_disease'
```
 
 Ensure that the required tables are created by running the FastAPI app, which will automatically generate the tables in the database.

5. Start the FastAPI backend:
```
cd backend
uvicorn main:app --reload
```

6. Start the Streamlit frontend:
```
cd backend
streamlit run app.py
```
The frontend will be accessible at `http://localhost:8501`.

## Training the Model

The pre-trained models are included in the `models/` directory, so no additional download is necessary. However, if you want to retrain the model, you can either use the public Kaggle notebook or download the same notebook from GitHub.

This project uses the [Plant Pathogens dataset](https://www.kaggle.com/datasets/sujallimje/plant-pathogens) , which is already linked in the Kaggle notebook but can also be downloaded for local use from GitHub. (Note: This Dataset is licensed under CC BY-NC-SA 4.0,  so The model trained using this dataset cannot be used for commercial purposes.)


## Steps to Train the Model:

1. **Option 1: Use Kaggle's Public Notebook** :
    - Directly Fork the [Plant Disease Classification Notebook](https://www.kaggle.com/code/anshkgoyal/plant-disease-classification) on Kaggle. This allows you to create your own copy of the notebook, ready to run and customize.
    - The dataset is pre-linked in the notebook, and you can use Kaggle's free GPU/TPU resources for training.
    
2. **Option 2: Use the GitHub Notebook** :
    - Download the `plant-disease-classification.ipynb` notebook from the GitHub repository and run it locally.
    - Install the necessary dependencies and ensure the dataset is properly downloaded and loaded.
    
    **Important Note**: The notebook in this GitHub repository is the same as the one uploaded on Kaggle. If you're running it locally, please be aware that:
    - You may need to manually install required libraries.
    - Some import statements might need adjustments due to differences between the Kaggle environment and your local setup.
    - While the notebook was originally run using TPU on Kaggle, the code is GPU-agnostic and can be run on different hardware setups with appropriate modifications.
    
3. **Training the Model** : 
    - Customize the model's hyperparameters (e.g., learning rate, batch size) in either environment.
    - Monitor the performance metrics (loss, accuracy) during training to ensure the model is learning effectively.
    - If using Kaggle, utilize the GPU/TPU to speed up training, especially for large datasets.
    
4. **Saving and Downloading Models** :
    - After training, save your model using `torch.save()` or `model.save()`, depending on the framework.
    - For Kaggle users, download the trained model files for local use. For GitHub users, simply save the model in your local directory.

By following these steps, you can train the model either on Kaggle or locally using the provided notebook. Remember to adjust your environment and code as necessary when running locally.



## Licensing Information

- The **code** in this repository is licensed under [Apache 2.0](https://github.com/AnshKGoyal/Plant-Disease-Classification/blob/main/LICENSE).
- The models and files found in the `model/` folder is licensed under [CC BY-NC-SA 4.0](https://github.com/AnshKGoyal/Plant-Disease-Classification/blob/main/model/LICENSE).
	- The **trained model** is derived from a dataset licensed under [CC BY-NC-SA 4.0](https://github.com/AnshKGoyal/Plant-Disease-Classification/blob/main/model/LICENSE) and is therefore licensed under the same terms. This model cannot be used for commercial purposes.
  - Official Website of CC BY-NC-SA 4.0 license is https://creativecommons.org/licenses/by-nc-sa/4.0/

## Contributing
---
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.
