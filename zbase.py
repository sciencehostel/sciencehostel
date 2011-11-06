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
import facebook
import logging
import cgi

from tornado.options import define, options

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    """
    1. check if user cookie set
    2. check if facebook cookie set, link
    """
    def get_current_user(self):
      user_id = self.get_secure_cookie("user")
      logging.info("user: %s", user_id) 
      if user_id != None:
        user = self.db.get('SELECT * from zuser where id = %s', user_id)
        return user
      user = self.get_facebook_user()
      logging.info(user)
      if user:
        self.set_cookie("utype", "fb")
        self.set_secure_cookie("user", str(user.id))
      return user

    def get_facebook_user(self):
      cookies = dict((n, self.cookies[n].value) for n in self.cookies.keys())
      logging.info('cookies: %s' % cookies)
      cookie = facebook.get_user_from_cookie(
          cookies, options.facebook_app_id, options.facebook_app_secret)
      logging.info('cookie: %s' % cookie)
      if not cookie: return None

      logging.info(cookie)
      if not cookie:
        return None
      # get or create entry in zuser
      user = self.db.get("SELECT * FROM zuser WHERE fb_uid = %s", cookie["uid"])
      if not user:
        logging.info("user not present")
        graph = facebook.GraphAPI(cookie["access_token"])
        profile = graph.get_object("me")

        # create entry
        self.db.execute(
            "REPLACE INTO zuser (name, fb_uid) "
            "VALUES (%s,%s)", profile["name"], cookie["uid"])
        user = self.db.get("SELECT * FROM zuser WHERE fb_uid = %s", cookie["uid"])
      return user

class AuthLoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", login_msg=None, current_header='header_login', options=options)

    def post(self):
        login_msg = None
        if self.get_argument("username",None) is None or self.get_argument("password",None) is None:
          self.render("login.html", login_msg="missing username or password")
          return
        # verify password
        user = self.db.get("SELECT * from zuser where username = %s", self.get_argument("username"))
        if user is None:
          self.render("login.html", login_msg="unknown user")
          return

        if user.password != self.get_argument("password"):
          self.render("login.html", login_msg="incorrect password", current_header='header_login')
          return

        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.set_cookie("utype", "science")
        self.redirect(self.get_argument("next", "/"))

class RegisterHandler(BaseHandler):
    def post(self):
        register_msg = None
        print self.request
        if self.get_argument("username",None) is None or self.get_argument("password1",None) is None or self.get_argument("password2",None) is None:
          self.render("register.html", register_msg="missing arguments", current_header="header_register")
          return
        if self.get_argument("password1") != self.get_argument("password2"):
          self.render("register.html", register_msg="passowrds dont match", current_header="header_register")
          return

        # create new user
        user = self.db.get("SELECT * from zuser where username = %s", self.get_argument("username"))
        if user is not None:
          self.render("register.html", register_msg="user exists", curent_header="header_register")
          return
        self.db.execute("INSERT INTO zuser (username, password, name, email ) VALUES(%s,%s,%s,%s)", self.get_argument("username"), self.get_argument("password1"), self.get_argument("name",None), self.get_argument("email",None))
        user = self.db.get("SELECT * from zuser where username = %s", self.get_argument("username"))
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.set_cookie("utype", "science")
        self.redirect(self.get_argument("next", "/"))

    def get(self):
        self.render("register.html", register_msg=None, current_header="header_register")

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


