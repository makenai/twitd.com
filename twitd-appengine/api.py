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
		tweet = Tweet(
			key_name          = "twitter_%s" % self.request.get('id'),
			id                = int( self.request.get('id') ),
			from_user         = self.request.get('from_user'),
			from_user_lc      = self.request.get('from_user').lower(),
			text              = self.request.get('text'),
			profile_image_url = self.request.get('profile_image_url'),
			created_at        = created_at,
			created_date      = created_at.date()
		)
		tweet.put()
		self.response.out.write( simplejson.dumps( tweet.to_dict() ) )

class AddToThread(webapp.RequestHandler):
	def post(self):
		tweet = Tweet.get( self.request.get('thread_id') )
		if tweet:
			retweet = ReTweet(
				key_name          = "twitter_%s" % self.request.get('id'),
				id                = int( self.request.get('id') ),
				from_user         = self.request.get('from_user'),
				from_user_lc      = self.request.get('from_user').lower(),
				text              = self.request.get('text'),
				profile_image_url = self.request.get('profile_image_url'),
				created_at        = datetime.strptime( self.request.get('created_at'), Tweet.DATE_FMT ),
				retweet_of		  = tweet
			)
			retweet.put()
			tweet.retweet_count = tweet.retweet_set.count()
			tweet.retweet_grade  = tweet.calc_grade()
			tweet.put()
			self.response.out.write( simplejson.dumps( retweet.to_dict() ) )
		
class ThreadList(webapp.RequestHandler):
	def get(self):
		tweet_query = Tweet.all().order('-created_at')
		user = self.request.get('user')
		if user:
			tweet_query.filter( 'from_user_lc =', user.lower() )
		tweets = [ tweet.to_dict() for tweet in tweet_query.fetch(100) ]
		self.response.out.write( simplejson.dumps(tweets) )
		
application = webapp.WSGIApplication([('/api/create_thread', CreateThread),
									  ('/api/add_to_thread', AddToThread),
									  ('/api/threads', ThreadList)],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()