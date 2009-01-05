$:.unshift File.join( File.dirname(__FILE__), 'lib' )
require 'rubygems'
require 'twitd'
require 'twitter'
require 'yaml'
require 'pidify'

class TwitdBot
end

if __FILE__ == $0
  
  exit if Pidify.running?
  
  Pidify.delete_pid if Pidify.pid_exists?
  
  Pidify.start
  
  # Production = http://re.twitd.com/api
  api_endpoint = ARGV[0] || 'http://localhost:8080/api'
  twitd = Twitd.new( api_endpoint )
  
  since_id = File.open('since_id.txt').read rescue nil  
  
  tweets = since_id ? Twitter.search( 'RT', :since_id => since_id ) : 
                      Twitter.search( 'RT', :max_pages => 1 )
  max_id = 0
  tweets.each do |tweet|

    if tweet['id'] > max_id
      max_id = tweet['id']
    end

    next unless matches = tweet['text'].match(/\brt\s+@(\w+):?\s+(.*)/i)
    user, text = matches[1], matches[2]
    next unless Twitter.user_exists?( user )
        
    if thread = twitd.get_thread( user, text )
      puts "Found #{thread['text']}"
      rt = twitd.add_to_thread( thread['key'], tweet )
      puts "  |- #{rt['text']}\n\n"
    else
      # Make a new thread
      original = twitd.find_original_tweet( user, text )
      if original
        thread = twitd.create_thread( original )
        puts "Created #{thread['text']}"
        rt = twitd.add_to_thread( thread['key'], tweet )
        puts "  |- #{rt['text']}\n\n"
      else
        puts "*** Could not find original for #{user}: #{text}\n\n"
      end
    end
    
  end
  
  File.open('since_id.txt','w') do |f|
    f.print max_id
  end
  
  Pidify.stop
  
end
