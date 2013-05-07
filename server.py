"""Sources 
https://gist.github.com/dbr/3304597

"""

import os

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.redirect("/static/map.html")

settings = {
  'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), ""),
}
print settings

application = tornado.web.Application([
  (r"/", MainHandler),
  ],
  **settings)

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

