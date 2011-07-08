#!/usr/bin/env python
import os.path
import re
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

from tornado.options import define, options

define("host", default='10.112.61.66', help="run on the given host")
define("port", default=9090, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="science", help="database name")
define("mysql_user", default="zoodle", help="database user")
define("mysql_password", default="zoodle123", help="database password")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/institutes", InstitutesHandler),
            (r"/scientists", ScientistsHandler),
            (r"/addInstitutes", AddInstitutesHandler),
            (r"/joining", JoiningHandler),
            (r"/forgotpwd", ForgotPwdHandler),
            (r"/faq", FaqHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

class MainHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('index.html')

class LoginHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('login.html')

class InstitutesHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('institutes.html')

class AddInstitutesHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('addInstitutes.html')

class ScientistsHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('scientists.html')

class JoiningHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('joining.html')

class FaqHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('faq.html')

class ForgotPwdHandler(tornado.web.RequestHandler):

  def get(self):
    self.render('forgotpwd.html')

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
