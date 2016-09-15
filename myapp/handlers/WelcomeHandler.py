from BlogHandler import BlogHandler


class WelcomeHandler(BlogHandler):  # Only redirected here after signup
    def get(self):
        if self.user:  # user instance comes from parent handler's initialize
            self.render('welcome.html', user_name=self.user.name)
        else:
            self.redirect('/signup')
