import os
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Firebase initialize - Environment Variables से
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n').replace('\r', ''),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token"
})

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://api-exchange-d5afc-default-rtdb.firebaseio.com'
})

# ─────────────────────────────────────
# API FUNCTIONS
# ─────────────────────────────────────

def get_api(service_name):
    ref = db.reference(f'apis/{service_name}')
    return ref.get()

def save_api(service_name, url, param):
    ref = db.reference(f'apis/{service_name}')
    ref.set({
        'url': url,
        'param': param,
        'active': True,
        'created': str(datetime.now())
    })

def delete_api(service_name):
    ref = db.reference(f'apis/{service_name}')
    ref.delete()

def list_apis():
    ref = db.reference('apis')
    return ref.get() or {}

# ─────────────────────────────────────
# KEY FUNCTIONS
# ─────────────────────────────────────

def check_key(key, service_name):
    ref = db.reference(f'keys/{key}')
    data = ref.get()

    if not data:
        return False, "❌ Invalid Key"

    allowed = data.get('service', '')
    if allowed != service_name and allowed != 'all':
        return False, f"❌ यह Key {service_name} के लिए नहीं है"

    expiry = data.get('expiry', '')
    if expiry and datetime.now() > datetime.strptime(expiry, '%Y-%m-%d'):
        return False, "⏰ Key Expired हो गई"

    limit = data.get('limit', 0)
    used = data.get('used', 0)
    if limit > 0 and used >= limit:
        return False, "🚫 Usage Limit खत्म"

    ref.update({'used': used + 1})
    return True, "✅ Valid"

def create_key(key, service, days, limit):
    from datetime import timedelta
    expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    ref = db.reference(f'keys/{key}')
    ref.set({
        'key': key,
        'service': service,
        'expiry': expiry,
        'limit': limit,
        'used': 0,
        'created': str(datetime.now())
    })

def delete_key(key):
    ref = db.reference(f'keys/{key}')
    ref.delete()

def list_keys():
    ref = db.reference('keys')
    return ref.get() or {}
