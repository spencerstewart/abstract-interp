import os
import re
import webapp2
import jinja2
import hasher
import cgi
import urllib
import urllib2
import logging
import hasher
from handlers.MainPageHandler import MainPageHandler
from handlers.NewPostHandler import NewPostHandler
from handlers.EditPostHandler import EditPostHandler
from handlers.ViewPostHandler import ViewPostHandler
from handlers.LikeHandler import LikeHandler
from handlers.SignupHandler import SignupHandler
from handlers.LoginHandler import LoginHandler
from handlers.LogoutHandler import LogoutHandler
from handlers.WelcomeHandler import WelcomeHandler
from handlers.InstaAPIHandler import InstaAPIHandler
from handlers.EditCommentHandler import EditCommentHandler
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

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
