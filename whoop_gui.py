import tkinter as tk
from tkinter import scrolledtext
import webbrowser
import urllib.parse
import requests
import os
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
REDIRECT_URI = os.getenv("WHOOP_REDIRECT_URI")

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

def handle_submit():
    code = code_entry.get()
    tokens = exchange_code_for_token(code)
    access_token = tokens.get("access_token")

    if not access_token:
        output_box.insert(tk.END, "Error retrieving token.\n")
        return

    data = get_recovery(access_token)
    output_box.insert(tk.END, f"📊 Recovery Data:\n{data}\n\n")

# --- GUI ---
window = tk.Tk()
window.title("Whoop API Demo")

tk.Label(window, text="1. Click to log into Whoop:").pack()
tk.Button(window, text="Open Whoop Login", command=open_login_url).pack(pady=5)

tk.Label(window, text="2. Paste your ?code= here:").pack()
code_entry = tk.Entry(window, width=60)
code_entry.pack(pady=4)

tk.Button(window, text="Submit Code", command=handle_submit).pack(pady=5)

tk.Label(window, text="3. API Output:").pack()
output_box = scrolledtext.ScrolledText(window, width=70, height=15)
output_box.pack(pady=10)

window.mainloop()
