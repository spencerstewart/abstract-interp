import re
from BlogHandler import BlogHandler
from models.User import User
from google.appengine.ext import ndb


# Signup regex checks
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


class SignupHandler(BlogHandler):
    def get(self):
        if self.user:
            self.redirect('/')
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
            self.redirect('/welcome')
