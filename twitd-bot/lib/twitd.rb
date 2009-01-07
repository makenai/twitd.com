require 'rubygems'
require 'amatch'
require 'rest_client'
require 'cgi'
require 'json'
require 'twitter'

class Twitd
  
  def initialize( base_url )
    @base_url = base_url
  end
  
  def get_threads_for_user( user )
    # Get the last 100 threads associated with a particular user
    # TODO: Add timestamp
    json = RestClient.get( "#{@base_url}/threads?user=#{CGI.escape(user)}" )
    return JSON.parse( json )
  end
  
  def create_thread( tweet )
    # Create a new thread on twitd.com
    json = RestClient.post( "#{@base_url}/create_thread", tweet )
    return JSON.parse( json )    
  end

  def add_to_thread( thread_id, tweet )
    # Add a retweet to a tweet thread
    tweet['thread_id'] = thread_id
    json = RestClient.post( "#{@base_url}/add_to_thread", tweet )
    return JSON.parse( json )
  end
  
  def get_thread( user, text )
    tweets = get_threads_for_user( user )
    return find_closest_tweet( text, tweets )
  end
  
  def find_original_tweet( user, text )
    # Given a username and the text of the retweet, tries to find the original tweet
    # that it was a retweet of.
    # TODO: Handle retweets of retweets recursively
    tweets = Twitter.search( "from:#{user}", :max_pages => 1 )
    return find_closest_tweet( text, tweets )
  end
  
  private
  
  def normalize_string( str )
    str.downcase.gsub(/[^a-z0-9 ]/i,'').gsub(/\s+/,' ')
  end
  
  def find_closest_tweet( text, tweets )
    text_n = normalize_string( text )
    m = Amatch::Levenshtein.new( text_n )
    tweets.each do |t|
      t[:distance]  = m.search( normalize_string( t['text'] ) )
    end
    original  = tweets.sort { |a,b| a[:distance] <=> b[:distance] }.first   
    return original && original[:distance] > 20 ? nil : original
  end
  
end

if __FILE__ == $0
  
  twitd = Twitd.new('http://localhost:8080/api')
  twitd.get_threads_for_user('aparanjapE')
  
end