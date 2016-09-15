import os
import re
import webapp2
import jinja2
import cgi
import urllib
import urllib2
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from myapp.handlers.MainPageHandler import MainPageHandler
from myapp.handlers.NewPostHandler import NewPostHandler
from myapp.handlers.EditPostHandler import EditPostHandler
from myapp.handlers.ViewPostHandler import ViewPostHandler
from myapp.handlers.LikeHandler import LikeHandler
from myapp.handlers.SignupHandler import SignupHandler
from myapp.handlers.LoginHandler import LoginHandler
from myapp.handlers.LogoutHandler import LogoutHandler
from myapp.handlers.WelcomeHandler import WelcomeHandler
from myapp.handlers.InstaAPIHandler import InstaAPIHandler
from myapp.handlers.EditCommentHandler import EditCommentHandler


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
#
# import sys
# sys.path.append('/Users/spencer/Code/P3/blog-proj/handlers')


app = webapp2.WSGIApplication([('/', MainPageHandler),
                               ('/newpost', NewPostHandler),
                               ('/edit', EditPostHandler),
                               ('/post.*', ViewPostHandler),
                               ('/like', LikeHandler),
                               ('/signup', SignupHandler),
                               ('/login', LoginHandler),
                               ('/welcome', WelcomeHandler),
                               ('/logout', LogoutHandler),
                               ('/auth', InstaAPIHandler),
                               ('/editcomment', EditCommentHandler)
                               ], debug=True)
