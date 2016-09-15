import cgi

from google.appengine.ext import ndb

from basehandlers import BlogHandler
from loginhandler import login_required
from insta_api import InstaAPI
from myapp.functions import hasher
from myapp.models import Post, Comment, Like


def blog_key(name='default'):
    return ndb.Key('blogs', name)


class NewPostHandler(BlogHandler):
    @login_required
    def get(self):
        img_url = InstaAPI.get_rand_image_url()  # returns false on error
        if not img_url:
            self.redirect('/auth')
            return
        img_url_hash = hasher.make_img_url_hash(img_url)
        name = ""
        if self.user:
            name = self.user.name
        self.render('newpost.html', img_url=img_url, user_name=name,
                    img_url_hash=img_url_hash)

    @login_required
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        img_url = self.request.get('img_url')
        img_url_hash = self.request.get('img_url_hash')
        s_error = ''
        c_error = ''
        img_error = hasher.check_img_url_hash(
            img_url, img_url_hash)  # returns empty string if no error

        # Valid form data
        if (subject and content and
            img_url and not img_error):
            content = cgi.escape(content)
            content = content.replace('\n', '<br>')
            author = str(self.user.name)
            post = Post(parent=blog_key(), subject=subject, content=content,
                        author=author, img_url=img_url, like_count=0, likes=[])
            post_key = post.put()
            post_id = post_key.id()
            self.redirect('/post?post_id=' + str(post_id))

        # Erroneous form data
        else:
            if not subject:
                s_error = "Please include a subject for your submission"
            if not content:
                c_error = "Please include content with your submission"
            if img_error:
                self.write(img_error)
            self.render('newpost.html',
                        s_error=s_error, c_error=c_error,
                        subject=subject, content=content,
                        img_url=img_url, img_url_hash=img_url_hash)


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


class EditPostHandler(BlogHandler):
    def get(self):
        self.redirect('/')

    @login_required
    def post(self):
        if self.request.get('edit'):
            post_id = self.request.get('edit')
            post = Post.get_by_id(int(post_id), parent=blog_key())
            user_name = ""
            author = ""
            if self.user:
                user_name = self.user.name
                if user_name == post.author:
                    post.content = post.content.replace(
                        '<br>', '')  # remove <br>s
                    self.render('editpost.html', post=post)
                else:
                    self.redirect('/')  # must be post author to edit
        elif self.request.get('delete'):
            post_id = self.request.get('delete')
            post = Post.get_by_id(int(post_id), parent=blog_key())
            post.key.delete()
            self.redirect('/')
        elif self.request.get('cancel'):
            post_id = self.request.get('cancel')
            self.redirect('/post?post_id=' + post_id)
        elif self.request.get('update'):
            post_id = self.request.get('update')
            post = Post.get_by_id(int(post_id), parent=blog_key())
            subject = self.request.get('subject')
            content = self.request.get('content')
            content = cgi.escape(content)
            content = content.replace('\n', '<br>')
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/post?post_id=' + post_id)
