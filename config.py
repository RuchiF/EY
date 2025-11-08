import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///provider_directory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or ''
    NPI_API_KEY = os.environ.get('NPI_API_KEY') or ''
    
    # Processing Settings
    MAX_CONCURRENT_VALIDATIONS = 10
    VALIDATION_TIMEOUT = 300  # 5 minutes
    CONFIDENCE_THRESHOLD = 0.80
    
    # File Upload Settings
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

