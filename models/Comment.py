

class Comment(ndb.Model):
    author = ndb.StringProperty(required=True)
    post_id = ndb.StringProperty(required=True)
    comment = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
