from google.appengine.ext import ndb

from basehandlers import BlogHandler
from myapp.models import User


class LoginHandler(BlogHandler):
    def get(self):
        if self.user:
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        if username and password:
            u = User.login(username, password)
            if u:
                self.login(u)
                self.redirect('/')
        errors = {'login_error': 'Incorrect username/password combo',
                  'username': username}
        self.render('login.html', **errors)


class LogoutHandler(BlogHandler):
    def get(self):
        self.logout()  # Sets user_id cookie val to empty
        self.redirect('/')
