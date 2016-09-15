import webapp2
import urllib2
import json
import random
from models.Config import Config


class InstaAPI(webapp2.RequestHandler):
    """ Instagram API functions. """

    @classmethod
    def get_access_token(cls):
        config_info = list(Config.query().fetch(limit=1))
        if config_info:
            config = config_info[0]
            return config.access_token
        else:
            return False

    @classmethod
    def get_rand_image_url(cls):
        """ Gets a random image from 20 most recent images.

            Future Endpoint:
            https://api.instagram.com/v1/tags/
            {tag-name}/media/recent?access_token=ACCESS-TOKEN """

        if not cls.get_access_token():
            return False  # Caught by NewPostHandler function.
        else:
            endpoint = 'https://api.instagram.com/v1/users/self/media/recent/?access_token='
            url = endpoint + cls.get_access_token()
            response = urllib2.urlopen(url)
            data = json.load(response)  # JSON response with many img objects
            random_pic_num = random.randint(0, 19)
            return data['data'][random_pic_num]['images']['standard_resolution']['url']
