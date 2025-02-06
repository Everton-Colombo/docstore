# config.py
import os

class Config:
    # MongoDB URI from environment variable or default value
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/mydatabase')
    
    # Admin API key (should be set in your environment for production)
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', 'super-secret-admin-key')