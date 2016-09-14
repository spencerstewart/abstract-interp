from BlogHandler import BlogHandler
from models.Post import Post
from google.appengine.ext import ndb


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
