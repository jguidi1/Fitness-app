import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import urllib.parse
import requests
import os
from dotenv import load_dotenv
from flask import Flask, request
import threading

# --- Load environment variables ---
load_dotenv()
CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")  # should be http://localhost:5000/callback

# --- Flask setup ---
flask_app = Flask(__name__)

# Shared variable to store the OAuth code
oauth_code = None

@flask_app.route("/callback")
def callback():
    global oauth_code
    oauth_code = request.args.get("code")
    return "<h2>OAuth code received! You can return to the app.</h2>"

def run_flask():
    flask_app.run(port=5000)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# --- Tkinter GUI ---
def generate_login_url():
    base_url = "https://api.prod.whoop.com/oauth/oauth2/auth"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "read:recovery read:cycles read:workout read:sleep"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def open_login_url():
    url = generate_login_url()
    webbrowser.open(url)
    output_box.insert(tk.END, "🔹 Browser opened. Log in to Whoop...\n")

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

def get_recovery(access_token):
    url = "https://api.prod.whoop.com/developer/v1/recovery"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    return r.json()

def check_for_code():
    global oauth_code
    if oauth_code:
        output_box.insert(tk.END, f"✅ Code received: {oauth_code}\n")
        tokens = exchange_code_for_token(oauth_code)
        access_token = tokens.get("access_token")
        if access_token:
            data = get_recovery(access_token)
            output_box.insert(tk.END, f"📊 Recovery Data:\n{data}\n")
        else:
            output_box.insert(tk.END, f"❌ Failed to get access token.\n")
        oauth_code = None
    window.after(1000, check_for_code)

# --- GUI Layout ---
window = tk.Tk()
window.title("Whoop OAuth Demo")

tk.Label(window, text="1. Click to log into Whoop:").pack()
tk.Button(window, text="Open Whoop Login", command=open_login_url).pack(pady=5)

tk.Label(window, text="2. API Output:").pack()
output_box = scrolledtext.ScrolledText(window, width=70, height=20)
output_box.pack(pady=10)

# Start checking for OAuth code
window.after(1000, check_for_code)

window.mainloop()
