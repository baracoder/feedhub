# Availible feeds:
from feeds.default import Feed          # Feed(URL,TITLE,CSS_CLASS)
from feeds.twitter import TwitterFeed   # TwitterFeed(USERID)

LIMIT = 50
FEEDS = [
    # add your feeds here
    # examples:
    #TwitterFeed('55714996'),
    #Feed('http://plusfeed.appspot.com/105123658415843460405','google+','gplus'),
    #Feed('http://api.flickr.com/services/feeds/photos_public.gne?id=15622444@N04&lang=en-us&format=rss_200','flickr','flickr'),
]

