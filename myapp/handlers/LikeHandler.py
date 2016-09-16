from google.appengine.ext import ndb

from basehandlers import BlogHandler
from loginhandler import login_required
from myapp.models import Post
from myapp.models import Like


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class LikeHandler(BlogHandler):
    def like(self, post):
        like = Like(liked_by=self.user.name, parent=post.key)
        like.put()
        post.like_count = Like.query(ancestor=post.key).count()
        post.put()  # Update likes

    def already_liked(self, post):
        likes = Like.query(ancestor=post.key)
        if likes:
            for like in likes:
                if like.liked_by == self.user.name:
                    return True
            return False
        else:
            return True

    @login_required
    def post(self):
        """ Form action for likes. """
        post_id = self.request.get('liked')
        post = Post.by_id(int(post_id))
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
