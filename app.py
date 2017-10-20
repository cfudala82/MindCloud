from __future__ import print_function
import httplib2
import uritemplate

import os
import boto3
import datetime

import functools
import urllib.parse as urllib_parse
from urllib.parse import urlencode

# This should help with posting events to calendar

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

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
        return str(user_id)
        # lookup user in database
        # return user

  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri='http://localhost:5000/auth',
                code=self.get_argument('code'))
            # print(access)
            # Save the user with e.g. set_secure_cookie

            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            print(user)
            set_user = Person.create(name=user['name'], token=user)

            # is user created?
            # if true save token else save user and token
            #
            print("here is the user info:", user)
            self.set_secure_cookie("user-id", "set-user-id")
            # print('Cookie set!')
            self.redirect('page/profile.html', {})

        else:
            yield self.authorize_redirect(
                redirect_uri='http://localhost:5000/auth',
                client_id="1077705632035-fppmfl90a30ogk5c1udolng4muk2uf0g.apps.googleusercontent.com",
                scope=['profile', 'email', 'https://www.googleapis.com/auth/calendar'],
                response_type='code',
                # extra_params={'approval_prompt': 'auto'}
                )

class AddCalendarHandler (TemplateHandler):
    @tornado.web.authenticated
    def post(self):
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Google Calendar API Python Quickstart'

        user = self.current_user

        def get_credentials():
            """Gets valid user credentials from storage.

            If nothing has been stored, or if the stored credentials are invalid,
            the OAuth2 flow is completed to obtain the new credentials.

            Returns:
                Credentials, the obtained credential.
            """

# work on this from database
# get from database
            credentials = store.get()
            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
                flow.user_agent = APPLICATION_NAME
                if flags:
                    credentials = tools.run_flow(flow, store, flags)
                else:
                    credentials = tools.run(flow, store)
            return credentials

        """Shows basic usage of the Google Calendar API.

        Creates a Google Calendar API service object and outputs a list of the next
        10 events on the user's calendar.
        """
        event = self.get_body_argument('event')
        deadline = self.get_body_argument('deadline')
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        created_event = service.events().quickAdd(
            calendarId='primary',  text=event + deadline).execute()
            # created_event = service.events().quickAdd(
            #     calendarId='primary',  text='Deploy Mind Cloud October 21st 9am-6pm').execute()
        print(created_event['id'])
        #         calendarId='primary',  text=event + deadline).execute()
        #     print(created_event['id'])
        # main(self.get_body_argument('event'))
# here's for inserting events into google calendar

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
    # self.render_template(name, {'path': self.request.path})

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


def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/auth", GoogleOAuth2LoginHandler),
    (r"/cal", AddCalendarHandler),
    (r"/page/(.*)", PageHandler),
    # (r"/event", EventHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'})
  ], **SETTINGS)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(PORT, print("Now serving up your app on PORT: " + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
