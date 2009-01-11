from google.appengine.ext import webapp
import re

register = webapp.template.create_template_register()

urlchars = r'[A-Za-z0-9/:@_%~#=&\.\-\?]+'
url = r'["=]?((http|ftp|https):%s)' % urlchars

def autolink(text):
    """Replaces all URLs in the text with HTML hyperlinks."""
    regexp = re.compile(url, re.I|re.S)
    def replace(match):
        url = match.groups()[0]
        return '<a href="%s" rel="nofollow">%s</a>' % (url, url)
    text = regexp.subn(replace, text)[0]
    return text
register.filter( autolink )

def autolink_twitter(text):
    regexp = re.compile(r'\B@(\w+)')
    def replace(match):
        user = match.groups()[0]
        return '<a href="http://twitter.com/%s" rel="nofollow">@%s</a>' % (user, user)
    text = regexp.subn(replace, text)[0]
    return text
register.filter( autolink_twitter )
	
def unescape_html( str ):
	return str.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>'). \
		replace('&quot;','"').replace('&#39;',"'")
		
def truncate(s, width):
	if len(s) <= width:
		return s
	if s[width].isspace():
		return s[0:width]
	else:
		return s[0:width].rsplit(None, 1)[0]
		