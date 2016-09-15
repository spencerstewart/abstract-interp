from bloghandler import BlogHandler
from myapp.models import Post


class MainPageHandler(BlogHandler):
    """ Homepage. """

    def get(self, user_name=''):
        error = ''
        if self.request.get('error'):
            error = self.request.get('error')
        posts = Post.query()
        posts = posts.order(-Post.created)
        posts = posts.fetch(10)
        name = ""
        if self.user:
            user_name = self.user.name
        self.render('home.html', posts=posts,
                    user_name=user_name, error=error)
