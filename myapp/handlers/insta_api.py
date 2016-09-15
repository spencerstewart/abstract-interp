import webapp2
import urllib2
import urllib
import json
import random

from google.appengine.ext import ndb
from google.appengine.api import urlfetch

from myapp.models import Config
from basehandlers import BaseHandler


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


class InstaAPIHandler(BaseHandler):
    """ Handles Instagram API authorization. """

    insta_creds = {'client_id': 'c00f51ef61ab4ac8ac543ae906bf4fde',
                   'redirect_uri': 'http://localhost:8080/auth',  # CHANGE ME!!!
                   # use https://abstract-interp.appspot.com//auth for prod
                   # use http://localhost:8080//auth for dev
                   'client_secret': 'e3852dc82ace453bb30d2df7287e148b',
                   'grant_type': 'authorization_code'}

    def get(self):
        """ Links to Instagram and receives access_token.

            On the intial visit to this page,  information about
            authorizing the Instagram API is presented to the user
            along with a button to authorize this app. The
            button submits a GET request to the Instagram API. In turn,
            the Instagram API redirects to this page with a GET code
            parameter.

            When this pages receives the code parameter, it posts
            this code along with app ID parameters to Instagram's
            access_token endpoint. If everything checks out, Instagram
            returns an OAuth token packaged in JSON. We save this
            access_token as a Config entity in Google Datastore.
         """

        if self.request.get('code'):  # Receives code parameter from Instagram
            self.insta_creds['code'] = str(self.request.get('code'))
            url = 'https://api.instagram.com/oauth/access_token'
            try:
                form_data = urllib.urlencode(self.insta_creds)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                result = urlfetch.fetch(  # Uses GAE fetch method
                    url=url,
                    payload=form_data,
                    method=urlfetch.POST,
                    headers=headers)
                parsed_json = json.loads(result.content)
                config = Config(access_token=parsed_json['access_token'])
                config.put()  # Save access_token in db
                self.redirect('/')
            except urlfetch.Error:
                logging.exception('Caught exception fetching url')
        else:
            self.render('auth_link.html', **self.insta_creds)
