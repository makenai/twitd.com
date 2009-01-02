from google.appengine.ext import db
from google.appengine.ext import search

# { "text"=>"RT @abhayshete A gem from Kumar Gandharva http://tinyurl.com/7q7l4f", 
#   "to_user_id"=>nil, 
#   "from_user"=>"aparanjape", 
#   "id"=>1090262568, 
#   "from_user_id"=>2712632, 
#   "iso_language_code"=>"nl", 
#   "profile_image_url"=>"http://s3.amazonaws.com/twitter_production/profile_images/65877355/shaniwar-wada-pune_normal.jpg", 
#   "created_at"=>"Thu, 01 Jan 2009 18:35:05 +0000"}

# http://groups.google.com/group/google-appengine/browse_thread/thread/f64eacbd31629668/8dac5499bd58a6b7?lnk=gst&q=searchablemodel

class Tweet(search.SearchableModel):
	
	id                = db.IntegerProperty(required=True)
	from_user         = db.StringProperty(required=True)
	from_user_lc      = db.StringProperty(required=True)	
	text              = db.StringProperty(required=True,multiline=True)
	profile_image_url = db.StringProperty(required=True)
	created_at        = db.DateTimeProperty(required=True)
	retweet_count     = db.IntegerProperty(default=0)
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
				
class ReTweet(Tweet):
	retweet_of	= db.ReferenceProperty(Tweet)
	
	def to_dict(self):
		dict = Tweet.to_dict(self)
		dict['parent_id'] = self.retweet_of.id
		return dict
		
