import cgi

from google.appengine.ext import ndb

from basehandlers import BlogHandler
from myapp.functions import hasher
from myapp.models import Post
from myapp.models import Comment


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class EditCommentHandler(BlogHandler):
    def get(self):
        self.render('editcomment.html')

    def post(self):
        """ Actions to post, edit, and update comments on the post. """

        if self.user:
            user_name = self.user.name
            if self.request.get('comment'):  # Posting a comment
                comment = self.request.get('comment')  # comment content
                author = user_name
                post_id = self.request.get('post_id')
                comment = Comment(author=author, post_id=post_id,
                                  comment=comment)
                comment.put()
                self.redirect('/post?post_id=' + post_id)
            elif self.request.get('delete'):
                post_id = self.request.get('post_id')
                comment_id = int(self.request.get('delete'))
                comment_to_delete = Comment.get_by_id(comment_id)
                comment_to_delete.key.delete()
                self.redirect('/post?post_id=' + post_id)
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
                self.redirect('/post?post_id=' + comment_to_update.post_id)
            else:
                self.get()

        else:
            self.redirect('/login')
