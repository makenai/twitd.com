from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from calendar import monthcalendar
from tweet_pager import TweetPager
from models import *

class Twitd(webapp.RequestHandler):
	def get(self, timespan='hours', page=1):
		pager = TweetPager()
		template_data = {
			'tweets':    pager.get( timespan, page ),
			'timespan':  timespan,
			'page':      int(page),
			'next_page': len( pager.get( timespan, int(page) + 1 ) ) > 0 and int(page) + 1 or None,
			'prev_page': int(page) > 1 and int(page) - 1 or None,
			'timespans': [ 'hours', 'day', 'week', 'fortnight' ],
		}
		self.response.out.write(template.render('templates/main.html', template_data))
		
class Retweets(webapp.RequestHandler):
	def get(self, tweet_id):
		tweet = Tweet.get_by_key_name( "t%s" % tweet_id )
		if tweet:
			template_data = {
				'tweet': tweet
			}
			self.response.out.write(template.render('templates/retweets.html', template_data))
			
class Comments(webapp.RequestHandler):
	def get(self,tweet_id,title):
		tweet = Tweet.get_by_key_name( "t%s" % tweet_id )
		if tweet:
			template_data = {
			}
			self.response.out.write(template.render('templates/main.html', template_data))
		
class UserRanking(webapp.RequestHandler):
	def get(self):
		template_data = {
		}
		self.response.out.write(template.render('templates/main.html', template_data))

class UserTweets(webapp.RequestHandler):
	def get(self, username):
		user = TwitterUser.get_by_key_name( "u%s" % username.lower() )
		tweets = Tweet.all().filter('user =', user).order('-retweet_count').fetch(25)
		if user:
			template_data = {
				'tweets': tweets
			}
			self.response.out.write(template.render('templates/main.html', template_data))


webapp.template.register_template_library('stringutils')

application = webapp.WSGIApplication([
										('/', Twitd),
										('/(hours|day|week|fortnight)', Twitd),
									  	('/(hours|day|week|fortnight)/(\d+)', Twitd),
										('/retweets/(\d+)', Retweets),
										('/(\d+)/(.*)',Comments),
										('/ranking', UserRanking),
										('/user/(\w+)', UserTweets)
									 ],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()