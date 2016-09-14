class LogoutHandler(BlogHandler):
    def get(self):
        self.logout()  # Sets user_id cookie val to empty
        self.redirect('/blog')
