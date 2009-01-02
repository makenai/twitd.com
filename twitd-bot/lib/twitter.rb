require 'rubygems'
require 'rest_client'
require 'json'
require 'cgi'

class Twitter
  
  USERNAME = 'dmfail'
  PASSWORD = 'deemedfail'

  def self.search( term, options={} )
    # Search search.twitter.com for a specific search string
    query_params = "?q=#{CGI.escape(term)}&rpp=100"
    if options[:since_id]
      query_params += "&since_id=#{options[:since_id]}"
    end
    return do_search( query_params, options[:max_pages] )
  end
  
  def self.do_search( query_params, max_pages=nil )
    json = RestClient.get("http://search.twitter.com/search.json#{query_params}")
    tweets = JSON.parse( json )
    return tweets['results'] if max_pages && tweets['page'] >= max_pages
    if tweets['next_page']
      more_tweets = do_search( tweets['next_page'], max_pages ) 
      return tweets['results'] + more_tweets
    else
      return tweets['results']
    end        
  end

  def self.user_exists?( user )
    # Check if the specific user exists on twitter
    # TODO: Retry (sometimes 503)
    RestClient.get("http://#{USERNAME}:#{PASSWORD}@twitter.com/users/show/#{user}.json")
    return true
  rescue RestClient::ResourceNotFound
    return false
  end
  
end

if __FILE__ == $0
  Twitter.search( 'test', :max_pages => 3 )
end