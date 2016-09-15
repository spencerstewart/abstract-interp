import webapp2
from BaseHandler import BaseHandler
from models.User import User
from functions import hasher
from google.appengine.ext import ndb


# def blog_key(name='default'):
#     return ndb.Key('blogs', name)


class BlogHandler(BaseHandler):
    """ Contains convenience functions inherited by sub classes. """

    # def __init__(self):  # sets default parent key
    #     self.blog_key = ndb.Key('blogs', 'default')


    def set_secure_cookie(self, name, val):
        """ Sets a secure value for a cookie and adds to header. """
        secure_val = hasher.make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, secure_val))

    def read_secure_cookie(self, name):
        """ Returns original value of a secured cookie val. """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and hasher.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """ Loads logged-in user object. """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
