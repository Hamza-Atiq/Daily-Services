"""
Firebase Admin SDK initialization.
Provides a Firestore client for the entire backend.

Supports 3 ways to authenticate:
1. FIREBASE_SERVICE_ACCOUNT_JSON env var (JSON string - best for Railway/cloud)
2. FIREBASE_SERVICE_ACCOUNT_PATH env var (file path - local dev)
3. Application Default Credentials (GCP Cloud Run)
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

_app = None
_db = None


def get_db():
    """Get the Firestore database client. Initializes Firebase if not already done."""
    global _app, _db
    if _db is None:
        # Option 1: JSON string in env var (Railway / cloud platforms)
        sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if sa_json:
            cred = credentials.Certificate(json.loads(sa_json))
            _app = firebase_admin.initialize_app(cred)
        else:
            # Option 2: File path
            sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json")
            if os.path.exists(sa_path):
                cred = credentials.Certificate(sa_path)
                _app = firebase_admin.initialize_app(cred)
            else:
                # Option 3: Application Default Credentials (GCP Cloud Run)
                _app = firebase_admin.initialize_app()
        _db = firestore.client()
    return _db

