"""Sources 
https://gist.github.com/dbr/3304597

"""

import os

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.auth
import tornado.options
from datetime import datetime

import pymongo

import json
import urllib2

""" FB AUTH STUFF """

class FeedHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
  @tornado.web.asynchronous
  def get(self):
    accessToken = self.get_secure_cookie('access_token')
    if not accessToken:
      self.redirect('/auth/login')
      return
    
    self.facebook_request(
      "/me/feed",
      access_token=accessToken,
      callback=self.async_callback(self._on_facebook_user_feed))

  def _on_facebook_user_feed(self, response):
    name = self.get_secure_cookie('user_name')
    self.render('home.html', feed=response['data'] if response else [], name=name)

  @tornado.web.asynchronous
  def post(self):
    accessToken = self.get_secure_cookie('access_token')
    if not accessToken:
      self.redirect('/auth/login')

    userInput = self.get_argument('message')

    self.facebook_request(
      "/me/feed",
      post_args={'message': userInput},
      access_token=accessToken,
      callback=self.async_callback(self._on_facebook_post_status))

  def _on_facebook_post_status(self, response):
    self.redirect('/')


class LoginHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
  @tornado.web.asynchronous
  def get(self):
    userID = self.get_secure_cookie('user_id')

    if self.get_argument('code', None):
      self.get_authenticated_user(
        redirect_uri='http://dev-machine.com:8888/auth/login',
        client_id=self.settings['facebook_api_key'],
        client_secret=self.settings['facebook_secret'],
        code=self.get_argument('code'),
        callback=self.async_callback(self._on_facebook_login))
      return
    elif self.get_secure_cookie('access_token'):
      self.redirect('/')
      return
  
    self.authorize_redirect(
      redirect_uri='http://dev-machine.com:8888/auth/login',
      client_id=self.settings['facebook_api_key'],
      extra_params={'scope': 'read_stream,publish_stream'}
    )

  def _on_facebook_login(self, user):
    if not user:
      self.clear_all_cookies()
      raise tornado.web.HTTPError(500, 'Facebook authentication failed')

    self.set_secure_cookie('user_id', str(user['id']))
    self.set_secure_cookie('user_name', str(user['name']))
    self.set_secure_cookie('access_token', str(user['access_token']))
    self.redirect('/')

class LogoutHandler(tornado.web.RequestHandler):
  def get(self):
    self.clear_all_cookies()
    self.render('logout.html')

class FeedListItem(tornado.web.UIModule):
  def render(self, statusItem):
    dateFormatter = lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S+0000').strftime('%c')
    return self.render_string('entry.html', item=statusItem, format=dateFormatter)


""" MAIN APP STUFF """

congress_api_key = '50f025f2cbae45078f52d0be51f69027'

class MapHandler(tornado.web.RequestHandler):
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

"""
settings = {
  'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), ""),
}
print settings
"""
class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r'/', FeedHandler),
      (r'/auth/login', LoginHandler),
      (r'/auth/logout', LogoutHandler),
      (r'/map', MapHandler),
      (r'/location', LocationHandler)
    ]
    
    """template_path=os.path.join(os.path.dirname(__file__), 'templates')"""

    settings = {
      'facebook_api_key': '170198893144703',
      'facebook_secret': 'd987c07f66f9544845307655d3f25dfc',
      'cookie_secret': 'NTliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg==', 
      'template_path': 'templates',
      'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), ""),
      'ui_modules': {'FeedListItem': FeedListItem}
    }
    print settings
    tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
  app = Application()
  server = tornado.httpserver.HTTPServer(app)
  server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

