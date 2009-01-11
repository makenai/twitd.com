from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from tweet_pager import TweetPager
from models import *

class TweetRss(webapp.RequestHandler):
	def get(self, timespan):
		pager = TweetPager()
		items = [ {
			'title': "[%d retweets] %s" % ( tweet.retweet_count, tweet.text ),
			'link': "http://re.twitd.com%s" % tweet.comment_link(),
			'description': "%s: %s" % ( tweet.from_user(), tweet.text ),
			'pubdate': tweet.created_at.strftime( Tweet.DATE_FMT ),
			'guid': "http://re.twitd.com%s" % tweet.comment_link()
		} for tweet in pager.get( timespan, 1 ) ]
		template_data = {
			'title': "re.twit'd in the last %s" % timespan,
			'link': "http://re.twitd.com/%s" % timespan,
			'rss_link': "http://re.twitd.com/rss/%s.xml" % timespan,
			'description': "i'm in ur twitter, trackin' ur retweets!",
			'items': items
		}
		self.response.headers['Content-Type'] = 'application/xml'
		self.response.out.write(template.render('templates/rss.xml', template_data))

application = webapp.WSGIApplication([
										('/rss/(hours|day|week|fortnight).xml', TweetRss)
									 ],
                                     debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()