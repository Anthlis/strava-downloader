from flask_login import UserMixin
from app import db, login


class Athlete(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    profile = db.Column(db.Text)
    profile_medium = db.Column(db.Text)
    summit = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    access_token = db.Column(db.Text)
    expires_at = db.Column(db.Integer)
    expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.Text)
    token_type = db.Column(db.Text)


    def __repr__(self):
        return '<Athlete {} - {} >'.format(self.firstname, self.id)
    
@login.user_loader
def load_athlete(id):
    return Athlete.query.get(int(id))
    
