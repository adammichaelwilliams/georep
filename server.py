"""Sources 
https://gist.github.com/dbr/3304597

"""

import os

import tornado.ioloop
import tornado.web

import json
import urllib2

congress_api_key = '50f025f2cbae45078f52d0be51f69027'

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.redirect("/static/map.html")

class LocationHandler(tornado.web.RequestHandler):
  def post(self):
    lat = self.get_argument('lat')
    lng = self.get_argument('lng')
    address = self.get_argument('address')
    data = json.load(urllib2.urlopen('http://congress.api.sunlightfoundation.com/legislators/locate?latitude='+lat+'&longitude='+lng+'&apikey='+congress_api_key))
    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    pretty_data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    self.render('location.html', address=address, result_data=data['results'], pretty_data=pretty_data)

settings = {
  'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), ""),
}
print settings


application = tornado.web.Application(
  handlers = [(r"/", MainHandler),(r"/location", LocationHandler)],
  template_path=os.path.join(os.path.dirname(__file__), "templates"),
  **settings)

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

