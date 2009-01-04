from datetime import datetime, timedelta
from google.appengine.api import memcache
import logging
from models import *

class TweetPager:
	
	PER_PAGE   = 15
	MAX_PAGES  = 10
	CACHE_TIME = 120 # 2 minutes 
	
	TIMESPANS = {
		'hour':		 timedelta(hours=1),
		'day':		 timedelta(days=1),
		'week':		 timedelta(weeks=1),
		'fortnight': timedelta(weeks=2),
	}
	
	def rank_sort( a, b ):
		return int( b.retweet_count - a.retweet_count )
	rank_sort = staticmethod(rank_sort)
	
	def get( self, timespan, page ):
		if int(page) > self.MAX_PAGES: # Let's not go out of bounds..
			return []
		requested_key = "%s_%d" % ( timespan, int(page) )
		tweets = memcache.get( requested_key )
		if tweets is not None:
			logging.debug("Cache hit: %s", requested_key)
			return tweets
	  	else:	
			logging.debug("Cache miss: %s", requested_key)
			cutoff_date = datetime.now() - self.TIMESPANS[ timespan ]
			tweet_query = Tweet.all().filter( 'created_date >', cutoff_date )
			tweets = tweet_query.fetch(500)
			tweets.sort( TweetPager.rank_sort )
			tweet_pages = {}
			for page in range( 1, self.MAX_PAGES + 1 ):				
				start = ( int(page) - 1 ) * self.PER_PAGE
				end   = start + self.PER_PAGE
				key   = "%s_%d" % ( timespan, page )
				tweet_pages[ key ] = tweets[start:end]
			errors = memcache.set_multi( tweet_pages, self.CACHE_TIME )
			if errors:
				logging.error("Not able to set: %s", str(errors) )
			return tweet_pages[ requested_key ]