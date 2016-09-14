import os
import re
import webapp2
import jinja2
import hasher
import cgi
import urllib
import urllib2
import logging
import json
import random
from handlers.MainPageHandler import MainPageHandler

import sys
sys.path.append('/Users/spencer/Code/P3/blog-proj/handlers')

# import MainPageHandler
# from handlers.MainPageHandler import MainPageHandler
# from handlers import *

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# General Database Classes


class Config(ndb.Model):
    """ Holds access Instagram API authentication info. """

    access_token = ndb.StringProperty(required=True)


# Handlers
class BaseHandler(webapp2.RequestHandler):
    """ Superclass that provides convenient helper functions. """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(**kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class AuthHandler(BaseHandler):
    """ Handles Instagram API authorization. """

    insta_creds = {'client_id': 'c00f51ef61ab4ac8ac543ae906bf4fde',
                   'redirect_uri': 'http://localhost:8080/blog/auth',  # CHANGE ME!!!
                   # use https://abstract-interp.appspot.com/blog/auth for prod
                   # use http://localhost:8080/blog/auth for dev
                   'client_secret': 'e3852dc82ace453bb30d2df7287e148b',
                   'grant_type': 'authorization_code'}

    def get(self):
        """ Links to Instagram and receives access_token.

            On the intial visit to this page,  information about
            authorizing the Instagram API is presented to the user
            along with a button to authorize this app. The
            button submits a GET request to the Instagram API. In turn,
            the Instagram API redirects to this page with a GET code
            parameter.

            When this pages receives the code parameter, it posts
            this code along with app ID parameters to Instagram's
            access_token endpoint. If everything checks out, Instagram
            returns an OAuth token packaged in JSON. We save this
            access_token as a Config entity in Google Datastore.
         """

        if self.request.get('code'):  # Receives code parameter from Instagram
            self.insta_creds['code'] = str(self.request.get('code'))
            url = 'https://api.instagram.com/oauth/access_token'
            try:
                form_data = urllib.urlencode(self.insta_creds)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                result = urlfetch.fetch(  # Uses GAE fetch method
                    url=url,
                    payload=form_data,
                    method=urlfetch.POST,
                    headers=headers)
                parsed_json = json.loads(result.content)
                config = Config(access_token=parsed_json['access_token'])
                config.put()  # Save access_token in db
                self.redirect('/blog')
            except urlfetch.Error:
                logging.exception('Caught exception fetching url')
        else:
            self.render('auth_link.html', **self.insta_creds)


class BlogHandler(BaseHandler):
    """ Contains convenience functions inherited by sub classes. """

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


class InstaAPI(webapp2.RequestHandler):
    """ Instagram API functions. """

    @classmethod
    def get_access_token(cls):
        config_info = list(Config.query().fetch(limit=1))
        if config_info:
            config = config_info[0]
            return config.access_token
        else:
            return False

    @classmethod
    def get_rand_image_url(cls):
        """ Gets a random image from 20 most recent images.

            Future Endpoint:
            https://api.instagram.com/v1/tags/
            {tag-name}/media/recent?access_token=ACCESS-TOKEN """

        endpoint = 'https://api.instagram.com/v1/users/self/media/recent/?access_token='
        if not cls.get_access_token():
            return False  # Caught by NewPostHandler function.
        else:
            url = endpoint + cls.get_access_token()
            response = urllib2.urlopen(url)
            data = json.load(response)  # JSON response with many img objects
            random_pic_num = random.randint(0, 19)
            return data['data'][random_pic_num]['images']['standard_resolution']['url']


# Users Code

def users_key(group='default'):
    """ Defines default parent key for user entities. """
    return ndb.Key('users', group)


# Signup regex checks
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    signup_date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = cls.query().filter(cls.name == name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = hasher.make_pw_hash(name, pw)
        return cls(parent=users_key(),
                   name=name,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and hasher.valid_pw(name, pw, u.pw_hash):
            return u


class SignupHandler(BlogHandler):
    def get(self):
        if self.user:
            self.redirect('/blog')
        else:
            self.render('signup.html')

    def check_uname_avail(self, uname):
        if User.query(User.name == uname).get():
            return True
        else:
            return False

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = {}

        if not USER_RE.match(username):
            errors['username_error'] = 'Username does not meet requirements'
        elif self.check_uname_avail(username):
            errors['username_error'] = 'Username already exists, try another'
        if not PASS_RE.match(password):
            errors['password_error'] = 'Password does not meet requirements'
        if not password == verify:
            errors['verify_error'] = 'Passwords do not match'
        if email and not EMAIL_RE.match(email):
            errors['email_error'] = 'Email not formatted correctly'
        if errors:
            self.render('signup.html', username=username, email=email, **errors)
        else:
            u = User.register(username, password, email)
            u.put()
            self.login(u)
            self.redirect('/blog/welcome')


class WelcomeHandler(BlogHandler):  # Only redirected here after signup
    def get(self):
        if self.user:  # user instance comes from parent handler's initialize
            self.render('welcome.html', user_name=self.user.name)
        else:
            self.redirect('/blog/signup')


class LoginHandler(BlogHandler):
    def get(self):
        if self.user:
            self.redirect('/blog')
        else:
            self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        if username and password:
            u = User.login(username, password)
            if u:
                self.login(u)
                self.redirect('/blog')
        errors = {'login_error': 'Incorrect username/password combo',
                  'username': username}
        self.render('login.html', **errors)


class LogoutHandler(BlogHandler):
    def get(self):
        self.logout()  # Sets user_id cookie val to empty
        self.redirect('/blog')


# class MainPageHandler(BlogHandler):
#     """ Homepage. """
#
#     def get(self, user_name=''):
#         error = ''
#         if self.request.get('error'):
#             error = self.request.get('error')
#         posts = Post.query()
#         posts = posts.order(-Post.created)
#         posts = posts.fetch(10)
#         name = ""
#         if self.user:
#             user_name = self.user.name
#         self.render('home.html', posts=posts,
#                     user_name=user_name, error=error)


# Likes stuff
class LikeHandler(BlogHandler):
    def like(self, post):
        post.likes.append(str(self.user.name))
        post.like_count = len(post.likes)
        post.put()

    def already_liked(self, post):
        if post.likes:
            who_liked = post.likes
            if self.user.name in who_liked:
                return True
            else:
                return False
        else:
            return False

    def post(self):
        """ Form action for likes. """
        if self.user:  # Must be logged in to like a post.
            post_id = self.request.get('liked')
            post = Post.get_by_id(int(post_id), parent=blog_key())
            if not self.user.name == post.author:  # Must not be author
                if not self.already_liked(post):
                    self.like(post)
                    self.redirect('/blog')
                else:
                    error = "You already liked that item."
                    self.redirect('/blog?error=' + error)
            else:
                error = "You can't like your own posts."
                self.redirect('/blog?error=' + error)
        else:
            self.redirect('/blog/login')


# Post stuff
def blog_key(name='default'):
    return ndb.Key('blogs', name)


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    img_url = ndb.StringProperty(required=True)
    author = ndb.StringProperty(required=True)
    like_count = ndb.IntegerProperty()  # Can do at query level
    likes = ndb.StringProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)


class NewPostHandler(BlogHandler):
    def get(self):
        img_url = InstaAPI.get_rand_image_url()  # returns false on error
        if not img_url:
            self.redirect('/blog/auth')
            return
        img_url_hash = hasher.make_img_url_hash(img_url)
        name = ""
        if self.user:
            name = self.user.name
        self.render('newpost.html', img_url=img_url, user_name=name,
                    img_url_hash=img_url_hash)

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        img_url = self.request.get('img_url')
        img_url_hash = self.request.get('img_url_hash')
        s_error = ''
        c_error = ''
        img_error = hasher.check_img_url_hash(
            img_url, img_url_hash)  # returns empty string if no error

        # Valid form data
        if (subject and content and
            img_url and not img_error):
            content = cgi.escape(content)
            content = content.replace('\n', '<br>')
            author = str(self.user.name)
            post = Post(parent=blog_key(), subject=subject, content=content,
                        author=author, img_url=img_url, like_count=0, likes=[])
            post_key = post.put()
            post_id = post_key.id()
            self.redirect('/blog/post?post_id=' + str(post_id))

        # Erroneous form data
        else:
            if not subject:
                s_error = "Please include a subject for your submission"
            if not content:
                c_error = "Please include content with your submission"
            if img_error:
                self.write(img_error)
            self.render('newpost.html',
                        s_error=s_error, c_error=c_error,
                        subject=subject, content=content,
                        img_url=img_url, img_url_hash=img_url_hash)


class ViewPostHandler(BlogHandler):
    """ Viewing an individual post.
    """
    def get(self, **kw):
        post_id = self.request.get('post_id')
        post = Post.get_by_id(int(post_id), parent=blog_key())
        comments = Comment.query()
        comments = comments.filter(Comment.post_id == post_id)
        comments = comments.order(-Comment.created)
        comments = comments.fetch(5)
        user_name = ""
        user_is_author = False
        if self.user:
            user_name = self.user.name
            if post.author and user_name == post.author:
                user_is_author = True
        self.render('viewpost.html', post=post,
                    user_name=user_name, user_is_author=user_is_author,
                    comments=comments, **kw)

    def post(self):
        """ Actions to post, edit, and update comments on the post.
        """
        if self.user:
            user_name = self.user.name
            if self.request.get('comment'):
                comment = self.request.get('comment')  # comment content
                author = user_name
                post_id = self.request.get('post_id')
                comment = Comment(author=author, post_id=post_id,
                                  comment=comment)
                comment.put()
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('delete'):
                post_id = self.request.get('post_id')
                comment_id = int(self.request.get('delete'))
                comment_to_delete = Comment.get_by_id(comment_id)
                comment_to_delete.key.delete()
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('edit'):
                comment_id = int(self.request.get('edit'))
                comment_to_edit = Comment.get_by_id(comment_id)
                self.render('editcomment.html', comment=comment_to_edit,
                            user_name=user_name, comment_id=comment_id)
            elif self.request.get('update'):
                comment_id = int(self.request.get('update'))
                comment_to_update = Comment.get_by_id(comment_id)
                updated_comment_contents = self.request.get('updated-comment')
                updated_comment_contents = cgi.escape(
                    updated_comment_contents)
                comment_to_update.comment = updated_comment_contents
                comment_to_update.put()
                self.redirect('/blog/post?post_id=' + comment_to_update.post_id)
            else:
                self.get()

        else:
            self.redirect('/blog/login')


class Comment(ndb.Model):
    author = ndb.StringProperty(required=True)
    post_id = ndb.StringProperty(required=True)
    comment = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)


class EditCommentHandler(BlogHandler):
    def get(self):
        self.render('editcomment.html')


class EditPostHandler(BlogHandler):
        def get(self):
            self.redirect('/blog')

        def post(self):
            if self.request.get('edit'):
                post_id = self.request.get('edit')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                user_name = ""
                author = ""
                if self.user:
                    user_name = self.user.name
                    if user_name == post.author:
                        post.content = post.content.replace(
                            '<br>', '')  # remove <br>s
                        self.render('editpost.html', post=post)
                    else:
                        self.redirect('/blog')  # must be post author to edit
            elif self.request.get('delete'):
                post_id = self.request.get('delete')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                post.key.delete()
                self.redirect('/blog')
            elif self.request.get('cancel'):
                post_id = self.request.get('cancel')
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('update'):
                post_id = self.request.get('update')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                subject = self.request.get('subject')
                content = self.request.get('content')
                content = cgi.escape(content)
                content = content.replace('\n', '<br>')
                post.subject = subject
                post.content = content
                post.put()
                self.redirect('/blog/post?post_id=' + post_id)

app = webapp2.WSGIApplication([('/blog', MainPageHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/edit', EditPostHandler),
                               ('/blog/post.*', ViewPostHandler),
                               ('/blog/like', LikeHandler),
                               ('/blog/signup', SignupHandler),
                               ('/blog/login', LoginHandler),
                               ('/blog/welcome', WelcomeHandler),
                               ('/blog/logout', LogoutHandler),
                               ('/blog/auth', AuthHandler),
                               ('/blog/editcomment', EditCommentHandler)
                               ], debug=True)
