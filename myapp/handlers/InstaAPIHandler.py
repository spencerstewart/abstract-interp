import urllib
import json
from BaseHandler import BaseHandler
from myapp.models import Config
from google.appengine.ext import ndb
from google.appengine.api import urlfetch


class InstaAPIHandler(BaseHandler):
    """ Handles Instagram API authorization. """

    insta_creds = {'client_id': 'c00f51ef61ab4ac8ac543ae906bf4fde',
                   'redirect_uri': 'http://localhost:8080//auth',  # CHANGE ME!!!
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
