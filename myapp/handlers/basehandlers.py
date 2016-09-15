import webapp2
import os
import jinja2

from google.appengine.ext import ndb

from myapp.models import User
from myapp.functions import hasher

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    """ Superclass that provides convenient helper functions. """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(**kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


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
