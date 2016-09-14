from google.appengine.ext import ndb


class Config(ndb.Model):
    """ Holds access Instagram API authentication info. """

    access_token = ndb.StringProperty(required=True)
