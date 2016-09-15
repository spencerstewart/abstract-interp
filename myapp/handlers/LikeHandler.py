from google.appengine.ext import ndb

from basehandlers import BlogHandler
from loginhandler import login_required
from myapp.models import Post


def blog_key(name='default'):
    return ndb.Key('blogs', name)


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

    @login_required
    def post(self):
        """ Form action for likes. """
        post_id = self.request.get('liked')
        post = Post.get_by_id(int(post_id), parent=blog_key())
        if not self.user.name == post.author:  # Must not be author
            if not self.already_liked(post):
                self.like(post)
                self.redirect('/')
            else:
                error = "You already liked that item."
                self.redirect('/?error=' + error)
        else:
            error = "You can't like your own posts."
            self.redirect('/?error=' + error)
