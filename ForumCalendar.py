# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:35:31 2022

@author: Ramon
"""

import requests
import tkinter as tk
import customtkinter
import datetime
import os.path
import pickle
import customtkinter
import time 
import locale
import asyncio
from calendar_auth import authorize_calendar

from json import dumps
from datetime import datetime
from tkinter import messagebox

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)
result = service.calendarList().list().execute()
calendar_id = result['items'][-1]['id']
results = service.events().list(calendarId=calendar_id, timeZone='Europe/Amsterdam').execute()

locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')

# ----------------- FUNCTIONS -----------------
def fetch_films():
    """Fetch currently showing films and their URLs"""
    url = "https://forum.nl/nl/film/nu-te-zien"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching films: {e}")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    films = soup.find_all("a", href=True)

    film_list = {}
    for film in films:
        title_tag = film.find("h3", {"class": "title heading-5 hyphenate"})
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = film['href']
            if link.startswith("/"):
                link = "https://forum.nl" + link
            film_list[title] = link

    return film_list

def data_scraper(film_url):
    """Scrape dates and times for a selected film"""
    page = requests.get(film_url)
    soup = BeautifulSoup(page.content, "html.parser")
    calendar = soup.find_all("div", {"class": ["calendar-day not-overview", "calendar-day not-overview active"]})

    data_list = {"dates": {}}
    for day in calendar:
        date = day.find("h5", {"class": "date-title"}).get_text(strip=True)
        times = [x.get_text(strip=True) for x in day.find_all('div', attrs={'class': 'time item'})]
        data_list["dates"][date] = times
    return data_list

def update_films_dropdown():
    """Fetch films and populate the OptionMenu"""
    global films_data
    films_data = fetch_films()
    film_var.set("Select Film")
    menu = film_menu["menu"]
    menu.delete(0, "end")

    for title in films_data.keys():
        menu.add_command(label=title, command=lambda t=title: on_film_select(t))

def on_film_select(title):
    """Update info box and dropdowns when a film is selected"""
    film_var.set(title)
    info.delete("1.0", tk.END)

    url = films_data[title]
    film_data = data_scraper(url)

    # Populate info box
    for date, times in film_data["dates"].items():
        info.insert(tk.END, f"{date}:\n")
        for t in times:
            info.insert(tk.END, f"  {t}\n")

    # Update date dropdown
    optmenu_date['menu'].delete(0, 'end')
    for date in film_data["dates"]:
        optmenu_date['menu'].add_command(label=date, command=lambda d=date: on_date_select(d, film_data))

    if film_data["dates"]:
        first_date = list(film_data["dates"].keys())[0]
        on_date_select(first_date, film_data)

def on_date_select(date, film_data):
    """Update time dropdown based on selected date"""
    optmenu_date_var.set(date)
    optmenu_time['menu'].delete(0, 'end')
    for t in film_data["dates"][date]:
        optmenu_time['menu'].add_command(label=t, command=lambda tt=t: optmenu_time_var.set(tt))
    if film_data["dates"][date]:
        optmenu_time_var.set(film_data["dates"][date][0])

def on_create_event():
    """Callback for Create Event button"""
    film = film_var.get()
    date = optmenu_date_var.get()
    time_str = optmenu_time_var.get()

    if film in films_data and date != "Select Date" and time_str != "Select Time":
        film_url = films_data[film]
        film_data = data_scraper(film_url)

        try:
            # Combine date + time into datetime object
            today = datetime.now()
            year = str(today.year)
            start_dt = time_str[0:5]
            end_dt = time_str[6:]
            date_scrape = date + " " + year
    
            startdate = "%s %s" % (date_scrape, start_dt)
            enddate = "%s %s" % (date_scrape, end_dt)
    
            date_start = datetime.strptime(startdate, '%A %d %B %Y %H:%M')
            date_end = datetime.strptime(enddate, '%A %d %B %Y %H:%M')

            # Call the original create_event function
            # Ensure 'service' and 'calendar_id' are defined elsewhere
            create_event(date_start, date_end, film)
            messagebox.showinfo("Success", f"Event '{film}' added to Google Calendar!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create event: {e}")
    else:
        messagebox.showerror("Error", "Please select a film, date, and time first.")


def create_event(start_time, end_time, summary):
    """Creates choosen event in Google Calendar"""
    timezone = 'Europe/Amsterdam'
    event = {
      'summary': 'Forum - {}'.format(summary),
      'location': 'Groninger Forum, 9712 JG Groningen',
      'description': "Ramon gaat",
      'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
      'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
    }
    return service.events().insert(calendarId=calendar_id, body=event).execute()

# ----------------- TKINTER GUI ----------------- #
win = tk.Tk()
win.title("Forum Film Agenda")
win.geometry("800x500")

films_data = {}

### Fetch films button ###
fetch_btn = tk.Button(win, text="Fetch Films", command=update_films_dropdown)
fetch_btn.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

### Film dropdown menu ###
film_var = tk.StringVar()
film_var.set("Fetching films...")
film_menu = tk.OptionMenu(win, film_var, ())
film_menu.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

### Create an info text box do display all the dates and times of a given film ###
info = customtkinter.CTkTextbox(win, width=400, fg_color="gray10", text_color="#DCE4EE")
info.grid(row=3, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")

### Create an optionmenu to select a certain date ###
optmenu_date_var = tk.StringVar()
optmenu_date_var.set("Select Date")
optmenu_date = tk.OptionMenu(win, optmenu_date_var, ())
optmenu_date.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

### Create an optionmenu to select a certain time ###
optmenu_time_var = tk.StringVar()
optmenu_time_var.set("Select Time")
optmenu_time = tk.OptionMenu(win, optmenu_time_var, ())
optmenu_time.grid(row=1, column=2, padx=20, pady=20, sticky="nsew")

### Fetch films button ###
create_btn = tk.Button(win, text="Create Event", command=on_create_event)
create_btn.grid(row=4, column=2, padx=20, pady=20, sticky="nsew")

auth_btn = tk.Button(win, text="Authorize Calendar", command=authorize_calendar)
auth_btn.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

win.mainloop()