# abstract-interp
![A screenshot of the app](http://spencer.tech/abstract-interp-screenshot.jpg)

Multi-user blog that provides an image to interpret. Udacity Full Stack ND Project.

See an example installation here: [https://abstract-interp.appspot.com/blog](https://abstract-interp.appspot.com/blog)

Based on Google App Engine and Webapp2.

## Synopsis
Users post interpretations to a randomly given image. Once posted, other users can comment on the person's interpretation, too.
Users are able to edit and delete their posts and their comments.

Guests may view the posts and comments, but must create an account or sign in to add an interpretation of a photo (a post) or to comment.

## Set up
This app runs on Google App Engine (GAE), which uses Webapp2. Additionally, templating is provided through Jinja2.

To set this up to run locally, first make sure you have [GAE's SDK installed](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).

Then, either clone or download and unzip the project files into a directory.

### On a Mac
For the App Engine SDK on Mac, you'd want to open up a terminal and navigate to where you moved the project files.
Particularly, you should be in the same directory as the app.yaml file (this stores basic config info).

Once you've navigated on Terminal to the correct directory, start the local dev environment by typing:
`dev_appserver.py .`
Don't forget to include the period at the end!
