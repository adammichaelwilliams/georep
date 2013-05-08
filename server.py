"""Sources 
https://gist.github.com/dbr/3304597

"""

import os

import tornado.ioloop
import tornado.web

import json
import urllib2

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.redirect("/static/map.html")

settings = {
  'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), ""),
}
print settings

latitude = '42.280077'
longitude = '-83.74188199999998'
congress_api_key = '50f025f2cbae45078f52d0be51f69027'

data = json.load(urllib2.urlopen('http://congress.api.sunlightfoundation.com/legislators/locate?latitude='+latitude+'&longitude='+longitude+'&apikey='+congress_api_key))
print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

application = tornado.web.Application([
  (r"/", MainHandler),
  ],
  **settings)

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

