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
# Setup

ENV = Environment(
  loader=PackageLoader('app', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

PORT = int(os.environ.get('PORT', '5000'))


class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):
    # test it
#     @tornado.auth._auth_return_future
#     def get_authenticated_user2(self, redirect_uri, code, callback):
#         http = self.get_auth_http_client()
#         body = urllib_parse.urlencode({
#             "redirect_uri": redirect_uri,
#             "code": code,
#             "client_id": self.settings[self._OAUTH_SETTINGS_KEY]['key'],
#             "client_secret": self.settings[self._OAUTH_SETTINGS_KEY]['secret'],
#             "grant_type": "authorization_code",
#         })
#
#         http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
#                    functools.partial(self._on_access_token, callback),
#                    method="POST", headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=body,
#                    validate_cert=False)
#
#
#     @tornado.auth._auth_return_future
#     def oauth2_request2(self, url, callback, access_token=None,
#                        post_args=None, **args):
#         all_args = {}
#         if access_token:
#             all_args["access_token"] = access_token
#             all_args.update(args)
#
#         if all_args:
#             url += "?" + urllib_parse.urlencode(all_args)
#         callback = functools.partial(self._on_oauth2_request, callback)
#         http = self.get_auth_http_client()
#         if post_args is not None:
#             http.fetch(url, method="POST", body=urllib_parse.urlencode(post_args),
#                        callback=callback, validate_cert=False)
# # When we deploy, validate_cert=True hopefully.
#         else:
#             http.fetch(url, callback=callback, validate_cert=False)

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri='http://localhost:5000/auth',
                code=self.get_argument('code'))
            print(access)
            # Save the user with e.g. set_secure_cookie
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            # is user created?
            # if true save token else save user and token
            #
            # print(user)
            self.redirect('page/profile.html', {})

        else:
            yield self.authorize_redirect(
                redirect_uri='http://localhost:5000/auth',
                client_id="1077705632035-fppmfl90a30ogk5c1udolng4muk2uf0g.apps.googleusercontent.com",
                scope=['profile', 'email', 'https://www.googleapis.com/auth/calendar'],
                response_type='code',
                # extra_params={'approval_prompt': 'auto'}
                )
        SCOPES = 'https://www.googleapis.com/auth/calendar'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Google Calendar API Python Quickstart'

    def post(self):
        def get_credentials():
            """Gets valid user credentials from storage.

            If nothing has been stored, or if the stored credentials are invalid,
            the OAuth2 flow is completed to obtain the new credentials.

            Returns:
                Credentials, the obtained credential.
            """
            home_dir = os.path.expanduser('~')
            credential_dir = os.path.join(home_dir, '.credentials')
            if not os.path.exists(credential_dir):
                os.makedirs(credential_dir)
            credential_path = os.path.join(credential_dir,
                                           'calendar-python-quickstart.json')

# work on this from database
            # store = Storage(credential_path)
            store = Storage(credential_path)
            credentials = store.get()
            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
                flow.user_agent = APPLICATION_NAME
                if flags:
                    credentials = tools.run_flow(flow, store, flags)
                else: # Needed only for compatibility with Python 2.6
                    credentials = tools.run(flow, store)
                print('Storing credentials to ' + credential_path)
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
        # print('Getting the upcoming 10 events')
        created_event = service.events().quickAdd(
            calendarId='primary',  text=event + deadline).execute()
            # created_event = service.events().quickAdd(
            #     calendarId='primary',  text='Deploy Mind Cloud October 21st 9am-6pm').execute()
        print(created_event['id'])
        #         calendarId='primary',  text=event + deadline).execute()
        #     print(created_event['id'])
        # main(self.get_body_argument('event'))
# here's for inserting events into google calendar
# class EventHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
#     try:
#         import argparse
#         flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#     except ImportError:
#         flags = None
#
#     # If modifying these scopes, delete your previously saved credentials
#     # at ~/.credentials/calendar-python-quickstart.json
#     SCOPES = 'https://www.googleapis.com/auth/calendar'
#     CLIENT_SECRET_FILE = 'client_secret.json'
#     APPLICATION_NAME = 'Google Calendar API Python Quickstart'
#
#
#     def get_credentials():
#         """Gets valid user credentials from storage.
#
#         If nothing has been stored, or if the stored credentials are invalid,
#         the OAuth2 flow is completed to obtain the new credentials.
#
#         Returns:
#             Credentials, the obtained credential.
#         """
#         home_dir = os.path.expanduser('~')
#         credential_dir = os.path.join(home_dir, '.credentials')
#         if not os.path.exists(credential_dir):
#             os.makedirs(credential_dir)
#         credential_path = os.path.join(credential_dir,
#                                        'calendar-python-quickstart.json')
#
#         store = Storage(credential_path)
#         credentials = store.get()
#         if not credentials or credentials.invalid:
#             flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#             flow.user_agent = APPLICATION_NAME
#             if flags:
#                 credentials = tools.run_flow(flow, store, flags)
#             else: # Needed only for compatibility with Python 2.6
#                 credentials = tools.run(flow, store)
#             print('Storing credentials to ' + credential_path)
#         return credentials
#
#     def main():
#         """Shows basic usage of the Google Calendar API.
#
#         Creates a Google Calendar API service object and outputs a list of the next
#         10 events on the user's calendar.
#         """
#         credentials = get_credentials()
#         http = credentials.authorize(httplib2.Http())
#         service = discovery.build('calendar', 'v3', http=http)
#
#         now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#         print('Getting the upcoming 10 events')
#         created_event = service.events().quickAdd(
#             calendarId='primary',  text='Appointment at Somewhere on October 20th 10am-10:25am').execute()
#         print(created_event['id'])


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
    "autoreload": True
}


def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/auth", GoogleOAuth2LoginHandler),
    (r"/page/(.*)", PageHandler),
    # (r"/event", EventHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'})
  ], **SETTINGS)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(PORT, print("Now serving up your app on PORT: " + str(PORT)))
  tornado.ioloop.IOLoop.current().start()
