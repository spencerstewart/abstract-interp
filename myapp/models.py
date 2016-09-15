from google.appengine.ext import ndb
from functions import hasher


class BaseModel(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)


class Config(ndb.Model):
    """ Currently only holds access Instagram API auth info. """

    access_token = ndb.StringProperty(required=True)


class Comment(ndb.Model):
    author = ndb.StringProperty(required=True)
    post_id = ndb.StringProperty(required=True)
    comment = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

# def blog_key(name='default'):
#     return ndb.Key('blogs', name)


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    img_url = ndb.StringProperty(required=True)
    author = ndb.StringProperty(required=True)
    like_count = ndb.IntegerProperty()  # Can do at query level
    likes = ndb.StringProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)


# def users_key(group='default'):
#     """ Defines default parent key for user entities. """
#     return ndb.Key('users', group)


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    signup_date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = cls.query().filter(cls.name == name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = hasher.make_pw_hash(name, pw)
        return cls(parent=users_key(),
                   name=name,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and hasher.valid_pw(name, pw, u.pw_hash):
            return u
