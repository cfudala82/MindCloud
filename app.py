#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log
import json
import requests
import datetime

from jinja2 import \
  Environment, PackageLoader, select_autoescape

from models import mindCloud

ENV = Environment(
  loader=PackageLoader('mindCloud', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get (self):
    # render input form
    self.render_template("index.html", {})

  def post (self):
    # get city name
    # city_local = self.get_body_argument('city')
    # print(city_local)
    # # lookup the weather
    # # city_data = json.loads(city.list.jason)
    #
    # APIKEY = 'c8b0d1c9bbed3bd8975048f2f3f5b019'
    # #r = requests.get("http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(city_local, APIKEY))
    # #data_local = json.loads(r.text)
    # timestamp = datetime.datetime.utcnow()
    #     # get city name
    # old = timestamp - datetime.timedelta(minutes=15)
    #
    # # city in database
    # try:
    #     weather_data = WeatherApp.select().where(WeatherApp.city == city_local).where(WeatherApp.created >= old).get()
    #     data_local = weather_data.data
    #     print("from database")
    # # api call if not in database
    # except:
    #     r = requests.get("http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}".format(city_local, APIKEY))
    #     data_local = json.loads(r.text)
    #     weather_data = WeatherApp.create(city = city_local, data = data_local, created = timestamp)
    #     print(r.json())
    #     #weather_data.save()


    self.render_template("index.html", {'data': data_local })
    # render the weather data

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)",
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()
