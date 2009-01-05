# = Pidify
#
# == Synopsis
#
# A Ruby module to simplify storing and deleting the PID of a running program.
# It also provides the ability to kill a running program whose PID it has
# already saved.  This allows a program to check if there is currently another
# running instance of itself, and give it the ability to kill that instance
# based on PID.
#
# Note that this does no special process checking and relies solely on the PID
# files it creates and maintains. 
#
# See Pidify for more information and examples.
#
# == Website
#
# Documentation:
# http://pidify.rubyforge.org/
#
# Rubyforge page and Download:
# http://rubyforge.org/projects/pidify/
# 
# == Requirements
#
# - Ruby 1.8
# - Pathname module
#
# == Author
# Payton Swick, 2005
#
# == License
# Creative Commons Attribution
# http://creativecommons.org/licenses/by/2.0/
#

# Use the module methods in Pidify to save/delete the PID of a running script,
# or kill a running script using a saved PID.
#
# Example:
#   require 'pidify'
#   Pidify.running?  # => false
#   Pidify.start
#   Pidify.running?  # => true
#   puts "I am running with PID #{Pidify.pid}!"
#   Pidify.stop
#   Pidify.running?  # => false
#
# A more useful example:
#   require 'pidify'
#   Signal.trap('INT') { Pidify.stop; exit }
#   module Doer
#     def self.start
#       puts "starting"
#       Pidify.start_as_daemon
#       loop do
#         puts "hello world"
#         sleep 1
#       end
#     end
#   end
#   if ARGV.include? 'stop'
#     Pidify.stop 
#     puts "Daemon stopped."
#   else
#     puts "Daemon starting."
#     Doer.start
#   end
#
module Pidify
  require 'pathname'
  @pid_directory = Pathname.new("/tmp")
  @file_name = $0
  
  class << self
    # Returns the Pathname of the PID storage directory (defaults to /var/run).
    def pid_directory
      @pid_directory
    end

    # Sets the PID storage directory (defaults to /var/run).  Be VERY CAREFUL
    # using this, as delete_pid will try to delete whatever file it thinks is
    # the pid_file for this script in the pid_directory.  It's probably a good
    # idea not to change this at all.
    def pid_directory=(dir)
      @pid_directory = Pathname.new(dir) unless dir.kind_of? Pathname
      @pid_directory = dir if dir.kind_of? Pathname
    end

    # Returns the PID filename as a Pathname.
    def pid_file
      @pid_directory + (Pathname.new(@file_name).basename.to_s+'.pid')
    end

    # Returns true if the pid_file exists for this script.
    def pid_exists?
      return FileTest.exists?(pid_file)
    end

    # Returns true if the process using pid is running.
    def running?
      return false unless pid_exists?
      begin
        Process::kill 0, pid
        true
      rescue Errno::ESRCH
        false
      end 
    end

    # Returns the PID stored in the pid_file (not necessarily the PID of this
    # script).  Returns nil if no PID exists or if there is a problem with the
    # read.
    def pid
      return nil unless pid_exists?
      dpid = nil
      begin
        File.open(pid_file, File::RDONLY) { |file| dpid = file.gets.chomp if file.flock(File::LOCK_SH|File::LOCK_NB); file.flock(File::LOCK_UN) }
      rescue
        return nil
      end
      return dpid.to_i if dpid && dpid.to_i > 0
      nil
    end

    # Saves the PID of this script into the pid_file.  Automatically called by
    # start.  Returns nil if the pid file already exists.  Returns true if
    # successful, false if there was a write problem.
    def save_pid
      return nil if pid_exists?
      begin
        File.open(pid_file, File::CREAT|File::EXCL|File::WRONLY) { |file| file.puts $$ if file.flock(File::LOCK_EX); file.flock(File::LOCK_UN) }
        true
      rescue
        false
      end
    end

    # Deletes the PID file.  Calling stop calls this automatically, but will
    # also try to send a kill signal to the running process, if it is different
    # from this one.  BEWARE that this tries to delete whatever file is
    # returned by pid_file and does no error checking on it!  Returns true if
    # the delete was successful, false if there was an error, and nil if the
    # pid file doesn't exist.
    def delete_pid
      return nil unless pid_exists?
      begin
        # FIXME: lock first?
        File.delete(pid_file)
        true
      rescue
        false
      end
    end

    # Saves the PID of this script into the pid_file by calling save_pid.
    # Raises an exception if pid_exists? returns false.  Returns true if
    # successful.
    def start
      raise "Failed to start: already running (PID file exists)." if pid_exists?
      return true if save_pid
    end

    # Deletes the saved PID file and, if the PID belongs to a process different
    # from this script, sends kill signals to the saved PID using pid_end.
    # Returns true if the process was killed or false otherwise.
    def stop(signals=%w(SIGTERM SIGQUIT SIGKILL), secs_between_signal=4)
      return false unless pid_exists?
      unless running?
        delete_pid
        return true
      end
      pid = self.pid
      killed = true
      killed = pid_end(signals, secs_between_signal) if pid != $$
      delete_pid if killed == true
      killed
    end
    
    # Sends each kill signal to the saved PID, pausing for secs_between_signal
    # after each to check if it the process remains running.  Stops when the
    # process has ended or when all signals have been tried.  Returns true if
    # the process was killed or false otherwise.
    def pid_end(signals=%w(SIGTERM SIGQUIT SIGKILL), secs_between_signal=4)
      pid = self.pid
      signals = [ signals ].flatten.map{|sig| sig.to_s}
      existed = false
      signals.each do |sig|
        begin
          Process.kill(sig, pid)
          existed = true
        rescue Errno::ESRCH
          return (existed ? true : nil)
        end
        return true unless running?
        sleep secs_between_signal
        return true unless running?
      end
      not running?
    end 

    # Like Pidify.start, but first calls Pidify.daemonize.  Will fail and raise
    # an exception if Pidify.running? returns true.
    def start_as_daemon
      raise "Failed to start: already running." if running?
      daemonize
      start
    end

    # Daemonizes this process.  Does not automatically use a PID file.  If you
    # want to use a PID file, you must call Pidify.start after the call to
    # daemonize or use Pidify.start_as_daemon.
    def daemonize
      fork and exit
      Process.setsid
      Dir.chdir '/'
      File.umask 0000
      STDIN.reopen "/dev/null"
      STDOUT.reopen "/dev/null", "a"
      STDERR.reopen STDOUT
    end
  end
end
