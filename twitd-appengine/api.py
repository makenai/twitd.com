from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson
from datetime import datetime
from models import *
	
class CreateThread(webapp.RequestHandler):
	def post(self):
		created_at = datetime.strptime( self.request.get('created_at'), Tweet.DATE_FMT )
		user = TwitterUser.create_or_update(
		    id				  = self.request.get('from_user_id'),
			screen_name       = self.request.get('from_user'),
			profile_image_url = self.request.get('profile_image_url')
		)
		user.put()
		tweet = Tweet(
			key_name          = "t%s" % self.request.get('id'),
			id                = int( self.request.get('id') ),
			text              = self.request.get('text'),
			created_at        = created_at,
			created_date      = created_at.date(),
			user              = user
		)
		tweet.put()
		self.response.out.write( simplejson.dumps( tweet.to_dict() ) )

class AddToThread(webapp.RequestHandler):
	def post(self):
		tweet = Tweet.get( self.request.get('thread_id') )
		if tweet:
			user = TwitterUser.create_or_update(
			    id				  = self.request.get('from_user_id'),
				screen_name       = self.request.get('from_user'),
				profile_image_url = self.request.get('profile_image_url')
			)
			user.put()
			retweet = ReTweet(
				key_name          = "t%s" % self.request.get('id'),
				id                = int( self.request.get('id') ),
				text              = self.request.get('text'),
				created_at        = datetime.strptime( self.request.get('created_at'), Tweet.DATE_FMT ),
				retweet_of		  = tweet,
				user              = user
			)
			retweet.put()
			tweet.retweet_count = tweet.retweet_set.count()
			tweet.classify()
			tweet.put()
			self.response.out.write( simplejson.dumps( retweet.to_dict() ) )
		
class ThreadList(webapp.RequestHandler):
	def get(self):
		key_name = "u%s" % self.request.get('user').lower()
		user = TwitterUser.get_by_key_name( key_name )
		if user:
			tweets = [ tweet.to_dict() for tweet in Tweet.all().filter('user =', user).fetch(100) ]
		else:
			tweets = []
		self.response.out.write( simplejson.dumps(tweets) )
		
class Truncate(webapp.RequestHandler):
	def get(self):
		items = None
		model = self.request.get('model')
		if model == 'Tweet':
			for instance in Tweet.all():
			  instance.delete()
		elif model == 'ReTweet':
			for instance in ReTweet.all():
			  instance.delete()
		elif model == 'TwitterUser':
			for instance in TwitterUser.all():
			  instance.delete()		
				
application = webapp.WSGIApplication([('/api/create_thread', CreateThread),
									  ('/api/add_to_thread', AddToThread),
									  ('/api/threads', ThreadList),
								      ('/api/truncate', Truncate)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()