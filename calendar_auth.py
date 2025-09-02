import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tkinter import messagebox

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = "token.pkl"
CLIENT_SECRET_FILE = "client_secret.json"

def authorize_calendar():
    """OAuth flow for Google Calendar and save token.pkl"""
    creds = None

    # Load existing credentials
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Run OAuth flow if no valid credentials
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(TOKEN_PATH, 'wb') as token_file:
                pickle.dump(creds, token_file)
            messagebox.showinfo("Success", "Calendar authorized and token saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to authorize calendar:\n{e}")
    else:
        messagebox.showinfo("Info", "Calendar already authorized!")

    return creds