from google.appengine.ext import db
from google.appengine.ext import search
import urllib

# { "text"=>"RT @abhayshete A gem from Kumar Gandharva http://tinyurl.com/7q7l4f", 
#   "to_user_id"=>nil, 
#   "from_user"=>"aparanjape", 
#   "id"=>1090262568, 
#   "from_user_id"=>2712632, 
#   "iso_language_code"=>"nl", 
#   "profile_image_url"=>"http://s3.amazonaws.com/twitter_production/profile_images/65877355/shaniwar-wada-pune_normal.jpg", 
#   "created_at"=>"Thu, 01 Jan 2009 18:35:05 +0000"}

class BaseTweet(db.Model):
	
	id                = db.IntegerProperty(required=True)
	from_user         = db.StringProperty(required=True)
	from_user_lc      = db.StringProperty(required=True)	
	text              = db.StringProperty(required=True,multiline=True)
	profile_image_url = db.StringProperty(required=True)
	created_at        = db.DateTimeProperty(required=True)
	created_date      = db.DateProperty()

	DATE_FMT = '%a, %d %b %Y %H:%M:%S +0000'
	
	def to_dict(self):
		return {
			'key': str( self.key() ),
			'id': self.id,
			'from_user': self.from_user,
			'text': self.text,
			'profile_image_url': self.profile_image_url,
			'created_at': self.created_at.strftime( self.DATE_FMT )
		}

class Tweet(BaseTweet):
	
	retweet_count = db.IntegerProperty(default=0)
	over2         = db.BooleanProperty(default=False)
	over5		  = db.BooleanProperty(default=False)
	over10		  = db.BooleanProperty(default=False)
	
	def classify(self):
		self.over2  = self.retweet_count > 2
		self.over5  = self.retweet_count > 5
		self.over10 = self.retweet_count > 10

	def as_retweet(self):
		retweet = "RT @%s: %s" % ( self.from_user, self.text )
		return urllib.quote( retweet.encode('utf-8') )
				
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
		
