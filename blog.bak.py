import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(**kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainPageHandler(Handler):
    def get(self):
        # posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
        posts = Post.all()
        posts.order('-created')
        self.render('home.html', posts=posts)


class ViewPostHandler(Handler):
    def get(self):
        post_id = self.request.get('post_id')
        self.write(post_id)
        # posts = db.GqlQuery('SELECT * FROM Post WHERE ')


class NewPostHandler(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        s_error = ''
        c_error = ''

        if subject and content:
            post = Post(subject=subject, content=content)
            post.put()
            self.redirect('/blog/post/?post_id=')
        else:
            if not subject:
                s_error = "Please include a subject for your submission"
            if not content:
                c_error = "Please include content with your submission"
            self.render('newpost.html',
                        s_error=s_error, c_error=c_error,
                        subject=subject, content=content)

app = webapp2.WSGIApplication([('/blog', MainPageHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/post/.*', ViewPostHandler)
                               ], debug=True)
