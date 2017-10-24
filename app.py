from __future__ import print_function
import httplib2
import uritemplate

import os
import boto3
import json
import datetime

import functools
import urllib.parse as urllib_parse
from urllib.parse import urlencode

# This should help with posting events to calendar

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.client import AccessTokenCredentials

import tornado.ioloop
import tornado.web
import tornado.log
import tornado.auth

import json

from jinja2 import \
  Environment, PackageLoader, select_autoescape

from models import Person, Goals

ENV = Environment(
  loader=PackageLoader('app', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

PORT = int(os.environ.get('PORT', '5000'))


class TemplateHandler(tornado.web.RequestHandler):
  def get_current_user(self):
    user_id = self.get_secure_cookie("user-id")
    # print('Coookie', user_id)
    if user_id:
        # print('Current user_id:', user_id.decode())
        user = Person.select().where(Person.user_id == user_id.decode())[0]
        return user

  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                # redirect_uri='http://mind-cloud.logancodes.com/auth',
                redirect_uri='http://localhost:5000/auth',

                code=self.get_argument('code'))
            # print(access)
            # Save the user with e.g. set_secure_cookie

            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            print(user)

            person, created = Person.get_or_create(
                user_id=user['id'],
                user_email=user['email'],
                defaults={'name': user['name'], 'token': access}
            )
            if not created:
                person.token = access
                person.save()

            print("here is the user info:", user)
            self.set_secure_cookie("user-id", user['id'])
            print('Cookie set!')
            self.redirect('page/profile.html', {})

# I updated the redirect_uri for our deployment

        else:
            yield self.authorize_redirect(
                # redirect_uri='http://mind-cloud.logancodes.com/auth',
                redirect_uri='http://localhost:5000/auth',

                client_id="1077705632035-fppmfl90a30ogk5c1udolng4muk2uf0g.apps.googleusercontent.com",
                scope=['profile', 'email', 'https://www.googleapis.com/auth/calendar'],
                response_type='code',
                )

class RemindersHandler(TemplateHandler):
  @tornado.web.authenticated
  def get(self):
    email = self.current_user.user_email
    print(email)
    self.set_header("Content-Type", 'html')
    self.render_template('Reminders.html', {'email': email})

class GoalsHandler(TemplateHandler):
  @tornado.web.authenticated

  def get(self):
    name = self.current_user.name
    # user_id = int(self.current_user.user_id)
    user_id = int(self.current_user.brain_id)
    goals = Goals.select().where(Goals.person_id == user_id)
    print(goals)
    print('User name: ', name, ',', 'User id: ', user_id)
    self.set_header("Content-Type", 'html')
    self.render_template('goals.html', {'name': name, 'goals': goals})
  def post(self):
      name = self.current_user.name
      brain_id = self.current_user.brain_id
      SCOPES = 'https://www.googleapis.com/auth/calendar'
      APPLICATION_NAME = 'Mind Cloud'
      print(self.current_user.token)
      credentials = AccessTokenCredentials(self.current_user.token['access_token'], 'my agent/1.0')
      print(credentials.invalid)
      user_id = self.get_secure_cookie("user-id")
      user = Person.select().where(Person.user_id == user_id.decode())[0]
      event = self.get_body_argument('event')
      print(user_id)
      goal = Goals.create(
          person_id=brain_id,
          title=event
        )
      deadline = self.get_body_argument('deadline')
      http = credentials.authorize(httplib2.Http())
      service = discovery.build('calendar', 'v3', http=http)

      now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
      created_event = service.events().quickAdd(
          calendarId='primary',  text=event + ' ' + deadline).execute()
      print(created_event['id'])
      self.render_template('goals.html', {'name': name, 'goal': goal})

class MainHandler(TemplateHandler):
  def get(self):
    self.set_header("Content-Type", 'html')
    self.render_template('login.html', {})

class PageHandler(TemplateHandler):
  def post(self, page):
      pass
  def get(self, page):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page, {})

SETTINGS = {
    "google_oauth": {
        "key":
            "1077705632035-fppmfl90a30ogk5c1udolng4muk2uf0g.apps.googleusercontent.com",
        "secret":
            "MMV037-nEQO6_BF8CSLAg3M5"
    },
    "autoreload": True,
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "login_url": "/auth"
}

class AchievementsHandler(TemplateHandler):
  @tornado.web.authenticated
  def get (self):
    # finds a list of achievments
    achievments = (Goals
                   .select(Goals.achievement).limit(3)
                   .join(Person)
                   .where(self.current_user.id==Goals.person_id)
                   .order_by(+Goals.reminder))
    # gets the users name
    name = self.current_user.name
    # send a data for name and achievements to the web page
    self.render_template('achievements.html', {'name': name, 'achievments': achievments})

class MapPageHandler(TemplateHandler):
  @tornado.web.authenticated
  def get (self):

    self.render_template('mapPage.html', {})

    #{'goal': goal})

    #(r"/page/mapPage.html", MapPageHandler),
  def post (self):
    #comment = self.get_body_argument('comment')
    #print(comment)
    self.render_template('mapPage.html', {})





def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/auth", GoogleOAuth2LoginHandler),
    (r"/Reminders", RemindersHandler),
    (r"/page/achievements.html", AchievementsHandler),
    (r"/page/mapPage.html", MapPageHandler),
    (r"/goals", GoalsHandler),
    (r"/page/(.*)", PageHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'})
  ], **SETTINGS)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(PORT, print("Now serving up your app on PORT: " + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
