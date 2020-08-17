import os
import urllib

from flask import (render_template, 
                   redirect, 
                   request, 
                   flash, 
                   url_for)
from flask_login import current_user, login_user
import requests

from app import app


def authorize_url():
    """Generate authorization uri"""
    app_url = 'http://127.0.0.1'
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "response_type": "code",
        "redirect_uri": f"{app_url}:5000/authorization_successful",
        "scope": "read,profile:read_all,activity:read",
        "approval_prompt": "force"
    }
    values_url = urllib.parse.urlencode(params)
    base_url = 'https://www.strava.com/oauth/authorize'
    auth_url = base_url + '?' + values_url
    return auth_url

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/authorize")
def authorize():
    return redirect(authorize_url())

@app.route("/authorization_successful")
def authorization_successful():
    error = request.args.get('error')
    if error == 'access_denied':
        flash(f'You denied the required access for Strava Downloader to work')

        return redirect(url_for("index"))

    code = request.args.get('code')
    scope = request.args.get('scope')
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "client_secret": os.getenv('STRAVA_CLIENT_SECRET'),
        "code": code,
        "grant_type": "authorization_code"
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    
    authorization_response = r.json()
    first_name = authorization_response['athlete']['firstname']
    flash(f'authorization was successful ')

    return render_template("athlete.html", athlete=first_name)