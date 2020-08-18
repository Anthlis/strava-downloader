
from dateutil.parser import parse

from app.models import Athlete

def parse_response(response):
    return Athlete(id = response["athlete"]["id"],
    firstname = response["athlete"]["firstname"],
    lastname = response["athlete"]["lastname"],
    profile = response["athlete"]["profile"],
    profile_medium = response["athlete"]["profile_medium"],
    created_at = parse(response["athlete"]["created_at"]),
    access_token = response["access_token"],
    expires_at = response["expires_at"],
    expires_in = response["expires_in"],
    refresh_token = response["refresh_token"],
    token_type = response["token_type"])


