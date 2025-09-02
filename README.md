# ForumCalendar
A program that scrapes the Forum Groningen screened films, it makes the user able to select a film they want to attend which they can then add to their Google Calendar.

## Getting started

### Dependencies

Requires Python 3.x, BeautifulSoup (bs4), requests, customtkinter, google_api_python_client, google_auth_oauthlib, and protobuf. 

The `requirements.txt` lists all the libraries with their specified version in order to run the program, this can be installed using (ideally in a clean virtual environment); 
```sh 
pip install -r requirements.txt
```

### Installing
* Clone this repositroy and work within there.
* The Google APIs Client Library for Python uses the `client_secrets.json` file format for storing the `client_id`, `client_secret`, and other OAuth 2.0 parameters.
* Download and put the `client_secrets.json` file in the same folder where you have cloned this repository.

See [Creating authorization credentials](https://developers.google.com/identity/protocols/OAuth2WebServer#creatingcred) for how to obtain a `client_secrets.json` file.

### Executing program
* Execute the program by running;
```sh 
python3 ForumCalendar.py
```
The Authorize Calendar button will redirect to an authorization and permission website of Google in order to grant access to your own Google Calendar. The credentials are then saved in the token.pkl file. 

## Authors
Ramon Luichies
