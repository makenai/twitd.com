from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from calendar import monthcalendar
from tweet_pager import TweetPager
from models import *

class Twitd(webapp.RequestHandler):
	def get(self, timespan='day', page=1):
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
		
class Search(webapp.RequestHandler):
	def get(self):
		self.response.out.write("Search")

application = webapp.WSGIApplication([
										('/', Twitd),
										('/(hours|day|week|fortnight)', Twitd),										
									  	('/(hours|day|week|fortnight)/(\d+)', Twitd),
										('/search', Search)
									 ],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()