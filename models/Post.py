from google.appengine.ext import ndb


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    img_url = ndb.StringProperty(required=True)
    author = ndb.StringProperty(required=True)
    like_count = ndb.IntegerProperty()  # Can do at query level
    likes = ndb.StringProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
