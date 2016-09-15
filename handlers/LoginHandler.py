from BlogHandler import BlogHandler
from models.User import User
from google.appengine.ext import ndb


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
