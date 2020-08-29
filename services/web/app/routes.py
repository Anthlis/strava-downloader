import os
import urllib
from datetime import datetime
from collections import defaultdict

from flask import (render_template, 
                   redirect, 
                   request, 
                   flash, 
                   url_for,
                   make_response
                   )
from flask_login import current_user, login_user, logout_user, login_required
import requests
from dateutil.parser import parse
from stravaio import StravaIO, strava_oauth2
import pandas as pd

from app import app
from app import db
from app.models import Athlete
from app.utils import parse_response
from app.forms import SubmitDownload


def authorize_url():
    """Generate authorization uri"""
    app_url = 'http://0.0.0.0'
    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "response_type": "code",
        "redirect_uri": f"{app_url}/login",
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

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    error = request.args.get('error')
    if error == 'access_denied':
        flash('You denied the required access for Strava Downloader to work', 'danger')

        return redirect(url_for("index"))

    code = request.args.get('code')

    params = {
        "client_id": os.getenv('STRAVA_CLIENT_ID'),
        "client_secret": os.getenv('STRAVA_CLIENT_SECRET'),
        "code": code,
        "grant_type": "authorization_code"
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    
    authorization_response = r.json()
    first_name = authorization_response['athlete']['firstname']
    id = authorization_response["athlete"]['id']
    authenticated_athlete = Athlete.query.get(id)

    if not authenticated_athlete: 
        new_athlete = parse_response(authorization_response)
        db.session.add(new_athlete)
        db.session.commit()
    

    authenticated_athlete = Athlete.query.get(id)

    authenticated_athlete.firstname = authorization_response["athlete"]["firstname"]
    authenticated_athlete.lastname = authorization_response["athlete"]["lastname"]
    authenticated_athlete.profile = authorization_response["athlete"]["profile"]
    authenticated_athlete.profile_medium = authorization_response["athlete"]["profile_medium"]
    authenticated_athlete.created_at = parse(authorization_response["athlete"]["created_at"])
    authenticated_athlete.access_token = authorization_response["access_token"]
    authenticated_athlete.expires_at = authorization_response["expires_at"]
    authenticated_athlete.expires_in = authorization_response["expires_in"]
    authenticated_athlete.refresh_token = authorization_response["refresh_token"]
    authenticated_athlete.token_type = authorization_response["token_type"]

    db.session.commit()

    login_user(authenticated_athlete, remember=True)

    flash(f'Athlete successfully logged in your token expires in \
            {authenticated_athlete.minutes_to_expire()} minutes', 'success')

    return redirect(url_for('athlete', id=current_user.id))

@app.route("/logout")
def logout():
    logout_user()
    flash(f'User successfully logged out', 'success')
    return redirect(url_for("index"))

@app.route('/athlete/<id>', methods=['POST','GET'])
@login_required
def athlete(id):
    form = SubmitDownload()
    athlete = Athlete.query.filter_by(id=id).first_or_404()
    if athlete.invalid_token():
        return redirect(url_for("logout"))
    if form.validate_on_submit():

        date_from = form.dt.data.strftime('%Y-%m-%d')
        return redirect( url_for('download_csv', id=current_user.id, date_from=date_from))
        
    return render_template('athlete.html', athlete=athlete, form=form)

@app.route('/download_csv/<id>/<date_from>')
@login_required
def download_csv(id=None, date_from=None):
    # TODO 
    # refresh token logic if expired
    date_from = int(parse(date_from).timestamp())
    
    authenticated_athlete = Athlete.query.get(id)
    access_token = authenticated_athlete.access_token
    client = StravaIO(access_token=access_token)

    activities = client.get_logged_in_athlete_activities(after=date_from)

    df_data = defaultdict(list)

    for activity in activities:
        for k, v in activity.to_dict().items():
            df_data[k].append(v)

    df = pd.DataFrame(df_data)

    df.drop(columns=['athlete','map'], inplace=True)

    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=activities.csv"
    resp.headers["Content-Type"] = "text/csv"

    return resp   
