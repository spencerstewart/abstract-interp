import cgi

from google.appengine.ext import ndb

from basehandlers import BlogHandler
from myapp.functions import hasher
from myapp.models import Post
from myapp.models import Comment


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class ViewPostHandler(BlogHandler):
    """ Viewing an individual post. """

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
