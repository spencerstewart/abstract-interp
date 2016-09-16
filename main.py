import webapp2


from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from myapp.handlers.mainpagehandler import MainPageHandler
from myapp.handlers.posthandler import EditPostHandler, ViewPostHandler, NewPostHandler
from myapp.handlers.likehandler import LikeHandler
from myapp.handlers.signuphandler import SignupHandler, WelcomeHandler
from myapp.handlers.loginhandler import LoginHandler, LogoutHandler
from myapp.handlers.insta_api import InstaAPIHandler
from myapp.handlers.commenthandler import CommentHandler


# All handlers live in /myapp/handlers/module. See imports above.
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
                               ('/comment', CommentHandler)
                               ], debug=True)
