import cgi

from google.appengine.ext import ndb

from basehandlers import BlogHandler
from loginhandler import login_required
from myapp.functions import hasher
from myapp.models import Post
from myapp.models import Comment


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class CommentHandler(BlogHandler):
    def get(self):
        self.render('editcomment.html')

    @login_required
    def post(self):
        """ Actions to post, edit, and update comments on the post. """

        user_name = self.user.name
        # Post a comment
        if self.request.get('comment'):
            comment = self.request.get('comment')  # comment content
            author = user_name
            post_id = self.request.get('post_id')
            post = Post.by_id(int(post_id))
            comment = Comment(author=author,
                              comment=comment, parent=post.key)
            comment.put()
            self.redirect('/post?post_id=' + post_id)
        # Delete an existing comment
        elif self.request.get('delete'):
            post_id = self.request.get('post_id')
            post = Post.by_id(int(post_id))
            comment_id = int(self.request.get('delete'))
            comment_to_delete = Comment.get_by_id(comment_id, parent=post.key)
            comment_to_delete.key.delete()
            self.redirect('/post?post_id=' + post_id)
        # Edit an existing comment
        elif self.request.get('edit'):
            post_id = self.request.get('post_id')
            post = Post.by_id(int(post_id))
            if self.user.name == post.author:  # Verify user is author
                comment_id = int(self.request.get('edit'))
                comment_to_edit = Comment.get_by_id(comment_id, parent=post.key)
                self.render('editcomment.html', comment=comment_to_edit,
                            user_name=user_name, comment_id=comment_id,
                            post_id=post_id)
                return
            else:
                self.redirect(
                    '/post?post_id=' + post_id)  # Wish I could flash error msg

        elif self.request.get('update'):
            post_id = self.request.get('post_id')
            post = Post.by_id(int(post_id))
            comment_id = int(self.request.get('update'))
            comment_to_update = Comment.get_by_id(comment_id, parent=post.key)
            updated_comment_contents = self.request.get('updated-comment')
            updated_comment_contents = cgi.escape(
                updated_comment_contents)
            comment_to_update.comment = updated_comment_contents
            comment_to_update.put()
            self.redirect('/post?post_id=' + post_id)
        else:
            self.redirect('/')
