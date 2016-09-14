import cgi
from BlogHandler import BlogHandler
from functions import hasher
from models.Post import Post
from models.Comment import Comment
from google.appengine.ext import ndb


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class ViewPostHandler(BlogHandler):
    """ Viewing an individual post.
    """
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

    def post(self):
        """ Actions to post, edit, and update comments on the post.
        """
        if self.user:
            user_name = self.user.name
            if self.request.get('comment'):
                comment = self.request.get('comment')  # comment content
                author = user_name
                post_id = self.request.get('post_id')
                comment = Comment(author=author, post_id=post_id,
                                  comment=comment)
                comment.put()
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('delete'):
                post_id = self.request.get('post_id')
                comment_id = int(self.request.get('delete'))
                comment_to_delete = Comment.get_by_id(comment_id)
                comment_to_delete.key.delete()
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('edit'):
                comment_id = int(self.request.get('edit'))
                comment_to_edit = Comment.get_by_id(comment_id)
                self.render('editcomment.html', comment=comment_to_edit,
                            user_name=user_name, comment_id=comment_id)
            elif self.request.get('update'):
                comment_id = int(self.request.get('update'))
                comment_to_update = Comment.get_by_id(comment_id)
                updated_comment_contents = self.request.get('updated-comment')
                updated_comment_contents = cgi.escape(
                    updated_comment_contents)
                comment_to_update.comment = updated_comment_contents
                comment_to_update.put()
                self.redirect('/blog/post?post_id=' + comment_to_update.post_id)
            else:
                self.get()

        else:
            self.redirect('/blog/login')
