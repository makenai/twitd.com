from google.appengine.ext import db
from google.appengine.ext import search
from datetime import datetime, timedelta
from xml.sax import saxutils
import urllib

# { "profile_link_color":"0000FF",
# 	"description":"Software Engineer at Zappos.com -- check us out at http:\/\/www.zappos.com and http:\/\/twitter.zappos.com!",
# 	"profile_background_tile":true,
# 	"utc_offset":-28800,
# 	"created_at":"Sat Apr 14 04:07:19 +0000 2007",
# 	"followers_count":867,
# 	"favourites_count":10,
# 	"profile_sidebar_fill_color":"FFF7DF",
# 	"time_zone":"Pacific Time (US & Canada)",
# 	"statuses_count":2381,
# 	"profile_background_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_background_images\/2367577\/please_fix_small.png",
# 	"profile_sidebar_border_color":"B7E6C5",
# 	"profile_image_url":"http:\/\/s3.amazonaws.com\/twitter_production\/profile_images\/67520747\/Photo_29_normal.jpg",
# 	"url":"http:\/\/twitter.zappos.com\/",
# 	"name":"Pawel Szymczykowski",
# 	"protected":false,
# 	"status":{"in_reply_to_user_id":12408002,"truncated":false,"created_at":"Tue Jan 06 07:10:29 +0000 2009","favorited":false,"text":"@dendro Road trip? I'd be game!","id":1099012299,"in_reply_to_status_id":1098995214,"source":"web"},
# 	"screen_name":"makenai",
# 	"friends_count":891,
# 	"profile_background_color":"B7B7AF",
# 	"notifications":false,
# 	"following":false,
# 	"profile_text_color":"000000",
# 	"location":"Las Vegas",
# 	"id":4569381 }		

class TwitterUser(db.Model):
	id                = db.IntegerProperty(required=True)
	screen_name       = db.StringProperty(required=True)
	profile_image_url = db.StringProperty(required=True)
	updated_at        = db.DateTimeProperty(required=True)
	
	def recent_retweet_count( self, from_date ):
		cutoff = from_date - timedelta(hours=5)
		return ReTweet.all().filter('user =', self).filter('created_at >', cutoff).count(5)
		
	def has_retweeted( self, tweet ):
		return ReTweet.all().filter('user =', self).filter('retweet_of =', tweet).count(1) > 0
	
	@classmethod
	def create_or_update( self, **args ):
		key_name = "u%s" % args['screen_name'].lower()
		user     = TwitterUser.get_by_key_name( key_name )
		if user:
			user.screen_name       = args['screen_name']
			user.profile_image_url = args['profile_image_url']
			user.updated_at        = datetime.now()
		else:
			user = TwitterUser(
				key_name		   = key_name,
				id				   = int( args['id'] ),
				screen_name		   = args['screen_name'],
				profile_image_url  = args['profile_image_url'],
				updated_at		   = datetime.now()
			)
		return user
		
# { "text"=>"RT @abhayshete A gem from Kumar Gandharva http://tinyurl.com/7q7l4f", 
#   "to_user_id"=>nil, 
#   "from_user"=>"aparanjape", 
#   "id"=>1090262568, 
#   "from_user_id"=>2712632, 
#   "iso_language_code"=>"nl", 
#   "profile_image_url"=>"http://s3.amazonaws.com/twitter_production/profile_images/65877355/shaniwar-wada-pune_normal.jpg", 
#   "created_at"=>"Thu, 01 Jan 2009 18:35:05 +0000" }
	
class BaseTweet(db.Model):
	
	id                = db.IntegerProperty(required=True)
	user              = db.ReferenceProperty(TwitterUser)
	text              = db.StringProperty(required=True,multiline=True)
	created_at        = db.DateTimeProperty(required=True)

	DATE_FMT = '%a, %d %b %Y %H:%M:%S +0000'
	
	def to_dict(self):
		return {
			'key': str( self.key() ),
			'id': self.id,
			'from_user': self.user.screen_name,
			'text': self.text,
			'profile_image_url': self.user.profile_image_url,
			'created_at': self.created_at.strftime( self.DATE_FMT )
		}
		
	def from_user(self):
		return self.user.screen_name
		
	def profile_image_url(self):
		return self.user.profile_image_url	

class Tweet(BaseTweet):
	
	created_date  = db.DateProperty(required=True)
	retweet_count = db.IntegerProperty(default=0)
	over2         = db.BooleanProperty(default=False)
	over5         = db.BooleanProperty(default=False)
	over10		    = db.BooleanProperty(default=False)
	
	def classify(self):
		self.over2  = self.retweet_count > 2
		self.over5  = self.retweet_count > 5
		self.over10 = self.retweet_count > 10

	def as_retweet(self):
		retweet = "RT @%s: %s" % ( self.from_user(), self.text )
		return urllib.quote( saxutils.unescape( retweet.encode('utf-8') ) )
				
class ReTweet(BaseTweet):
	
	retweet_of	= db.ReferenceProperty(Tweet)
	
	def to_dict(self):
		dict = BaseTweet.to_dict(self)
		dict['parent_id'] = self.retweet_of.id
		return dict
		
class Comment(BaseTweet):

	comment_for	= db.ReferenceProperty(Tweet)

	def to_dict(self):
		dict = BaseTweet.to_dict(self)
		dict['parent_id'] = self.comment_for.id
		return dict		