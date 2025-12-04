import requests
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")

# STEP 1: Generate Login URL
def generate_login_url():
    base_url = "https://api.prod.whoop.com/oauth/oauth2/auth"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "read:recovery read:cycles read:workout read:sleep"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

# STEP 2: Exchange code → access token
def exchange_code_for_token(code):
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    r = requests.post(token_url, data=data)
    return r.json()

# STEP 3: Make an API call
def get_recovery(access_token):
    url = "https://api.prod.whoop.com/developer/v1/recovery" 
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    return r.json()

# Flow
login_url = generate_login_url()
print("\n👉 Open this URL in your browser to sign in:")
print(login_url)

code = input("\nPaste the 'code' from the URL here:\n> ")

tokens = exchange_code_for_token(code)
access_token = tokens["access_token"]

print("\n🔐 Access Token Obtained!")
print(access_token)

data = get_recovery(access_token)

print("\n📊 Your current recovery data:")
print(data)
