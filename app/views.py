from app import app
import jinja2
from apiclient.discovery import build
import json

from flask import Flask, url_for, redirect, session

from flask_login import (UserMixin, login_required, login_user, logout_user,
                         current_user)

from flask_googlelogin import GoogleLogin

googlelogin = GoogleLogin(app)

@app.route('/')
@app.route('/index')
def index():
    return "hi"
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()
