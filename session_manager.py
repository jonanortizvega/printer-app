import os
import json
from config import SESSION_FILE

def save_token(token):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"token": token}, f)

def load_token():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f).get("token")
    return None