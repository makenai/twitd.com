$:.unshift File.join( File.dirname(__FILE__), 'lib' )
require 'rubygems'
require 'twitd'
require 'twitter'
require 'yaml'

class TwitdBot
end

if __FILE__ == $0
  
  twitd = Twitd.new('http://re.twitd.com/api')
  
  tweets = Twitter.search( 'RT', :max_pages => 1 )
  tweets.each do |tweet|

    # TODO : RT might not always have to be at the beginning of the tweet
    next unless matches = tweet['text'].match(/^rt\s+@(\w+)\s+(.*)/i)
    user, text = matches[1], matches[2]
    next unless Twitter.user_exists?( user )
        
    if thread = twitd.get_thread( user, text )
      puts "Found #{thread['key']}"
      p twitd.add_to_thread( thread['key'], tweet )
    else
      # Make a new thread
      original = twitd.find_original_tweet( user, text )
      if original
        thread = twitd.create_thread( original )
        puts "Created #{thread['key']}"
        p twitd.add_to_thread( thread['key'], tweet )
      else
        puts "*** Could not find original for #{user}: #{text}"
      end
    end
    
  end
  
end