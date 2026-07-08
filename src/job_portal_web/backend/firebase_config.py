import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Path to the Firebase service account key
BASE_DIR = Path(__file__).resolve().parent
cred = credentials.Certificate(BASE_DIR / "firebase_key.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()