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
import logging
import tornado.template

from tornado.options import define, options
from zmail import *

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
            (r"/approveAddInstitutes", ApproveAddInstitutesHandler),
            (r"/admin", AdminHandler),
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

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class MainHandler(BaseHandler):

  def get(self):
    self.render('index.html')

class LoginHandler(BaseHandler):

  def get(self):
    self.render('login.html')

class InstitutesHandler(BaseHandler):

  def get(self):
    institutes = self.db.query('SELECT * from institute')
    self.render('institutes.html', institutes=institutes)

class AddInstitutesHandler(BaseHandler):

  def get(self):
    self.render('addInstitutes.html')

  def post(self):
    logging.info(self.request)
    institute_name = self.get_argument('institute_name', '')
    institute_desc = self.get_argument('institute_desc', '')
    institute_addr = self.get_argument('institute_addr', '')
    institute_host_name = self.get_argument('institute_host_name', '')
    institute_host_email = self.get_argument('institute_host_email', '')

    # write to db
    add_institute_id = self.db.execute(
            "INSERT INTO add_institute(institute_name, institute_desc, institute_addr, institute_host_name, institute_host_email) VALUES (%s,%s,%s,%s,%s)",
            institute_name, institute_desc, institute_addr, institute_host_name, institute_host_email)

    newrequest = self.db.get('SELECT * from add_institute where id = %s', str(add_institute_id))

    loader = tornado.template.Loader('templates/')
    email_note = loader.load("add_institute_email.html").generate(newrequest=newrequest)
    SendTo([institute_host_email], 'New Institute Request', email_note)
    self.write('yo')

class ApproveAddInstitutesHandler(BaseHandler):

  def post(self):
    logging.info(self.request)
    request_id = self.get_argument('request')
    approved = self.get_argument('approved')

    # update db
    if approved == 'true':
      state = 'approved'
    else:
      state = 'denied'
    self.db.execute(
            "UPDATE add_institute SET state=%s WHERE id=%s", state, request_id)

    newrequest = self.db.get('SELECT * from add_institute where id = %s', str(request_id))

    loader = tornado.template.Loader('templates/')
    if approved == 'true':
      email_note = loader.load("add_institute_approved_email.html").generate(newrequest=newrequest)
    else:
      email_note = loader.load("add_institute_denied_email.html").generate(newrequest=newrequest)

    SendTo([newrequest.institute_host_email], 'New Institute Request', email_note)
    self.write('yo')

class AdminHandler(BaseHandler):
  def get(self):
    requests = self.db.query('SELECT * from add_institute')
    self.render('admin.html', requests=requests)

class ScientistsHandler(BaseHandler):

  def get(self):
    scientists = self.db.query('SELECT * from scientist')
    self.render('scientists.html', scientists=scientists)

class JoiningHandler(BaseHandler):

  def get(self):
    self.render('joining.html')

class FaqHandler(BaseHandler):

  def get(self):
    self.render('faq.html')

class ForgotPwdHandler(BaseHandler):

  def get(self):
    self.render('forgotpwd.html')

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
