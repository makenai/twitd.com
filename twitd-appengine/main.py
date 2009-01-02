from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from calendar import monthcalendar
from models import *

class Twitd(webapp.RequestHandler):
	PER_PAGE = 25
	def get(self, page=1):
		tweet_query = Tweet.all().order('-created_date').order('-retweet_count')
		# Offsets don't work here? http://localhost:8080/401
		tweets = tweet_query.fetch(self.PER_PAGE, (int(page) - 1) * self.PER_PAGE)
		next_page_items = tweet_query.fetch(1, (int(page)) * self.PER_PAGE)
		template_data = {
			'tweets':    tweets,
			'page':      int(page),
			'next_page': len(next_page_items) > 0 and int(page) + 1 or None,
			'prev_page': int(page) > 1 and int(page) - 1 or None,
		}
		self.response.out.write(template.render('templates/main.html', template_data))
		
class Search(webapp.RequestHandler):
	def get(self):
		self.response.out.write("Search")

application = webapp.WSGIApplication([
										('/', Twitd),
									  	('/(\d+)', Twitd),
										('/search', Search)
									 ],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()