#!/usr/bin/python2.4
# -*- coding: utf-8 -*-

from xml.dom import minidom
import urllib2 
import time

from cgi import escape

from datetime import datetime

import sanitizer
USER_AGENT = 'Passiomatic Feedhub/0.5.1 <http://lab.passiomatic.com/feedhub/>'
    

try:
    import config
    FEEDS = config.FEEDS
except ImportError:
    print "Unable to find file config.py. Please rename config-sample.py first."
    FEEDS = []
    
    import sys; sys.exit(1)


def get_feed(url):
    
    #print 'Getting', url 

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', USER_AGENT)]
    
    request = opener.open(url)
    
    data = request.read()
    request.close()
    
    return data
    

# -----------------------------------------------------------


class Item(object): 
    def __repr__(self): return getattr(self, 'title', 'Untitled').encode('utf-8', 'replace')
        
    __str__ = __repr__



def _get_atom_entries(the_feed, document):
    
    entries = document.getElementsByTagName('entry')
    
    items = []
    
    for entry in entries:
        
        item = Item()        
        
        item.the_feed = the_feed
        item.url = entry.getElementsByTagName('link')[0].getAttribute('href')        
        item.id = entry.getElementsByTagName('id')[0].firstChild.nodeValue
        item.title = entry.getElementsByTagName('title')[0].firstChild.nodeValue
        
        item.teaser = entry.getElementsByTagName('content')[0].firstChild.nodeValue
        #item.teaser = entry.getElementsByTagName('summary')[0].firstChild.nodeValue

        date_published = entry.getElementsByTagName('published')[0].firstChild.nodeValue
        
        try:
            # 2008-10-27T11:06:52 (ignore time zone)
            date_published = datetime(*(time.strptime(date_published[:19], '%Y-%m-%dT%H:%M:%S')[0:6]))
        except ValueError:
            date_published = datetime.now()
        
        item.date_published = date_published
                        
        items.append(item)
        
    return items



class Category(object):  
    
    def __repr__(self): return getattr(self, 'title', 'Untitled').encode('utf-8', 'replace')
        
    __str__ = __repr__
    

def _get_rss_entries(the_feed, document):
    
    entries = document.getElementsByTagName('item')
    
    items = []
    
    for entry in entries:
        
        item = Item()        
        
        item.the_feed = the_feed
        item.url = entry.getElementsByTagName('link')[0].firstChild.nodeValue  
        item.id = entry.getElementsByTagName('guid')[0].firstChild.nodeValue
        
        item.title = entry.getElementsByTagName('title')[0].firstChild.nodeValue
        
        # @@TODO: get category
        #item.categories = entry.getElementsByTagName('category')
        
        #TODO: fix empty content
        #item.teaser = entry.getElementsByTagName('content')[0].firstChild.nodeValue
        item.teaser = ''
        #item.teaser = entry.getElementsByTagName('summary')[0].firstChild.nodeValue


        date_published = entry.getElementsByTagName('pubDate')[0].firstChild.nodeValue
            
        try:
            # Sun, 08 Feb 2009 22:48:25 (ignore time zone)
            date_published = datetime(*(time.strptime(date_published[:25], '%a, %d %b %Y %H:%M:%S')[0:6]))
        except ValueError:
            date_published = datetime.now()
        

        item.date_published = date_published
        
        items.append(item)
        
    return items
    
# -----------------------------------------------------------

def parse_feed(the_feed):
    
   
    try:
    	s = get_feed(the_feed[2])    
    except urllib2.URLError:
    	return []
               
    document = minidom.parseString(s)    
    
    #print document.documentElement 
    
    # flavor? 
    if the_feed[3] == 'atom':
        items = _get_atom_entries(the_feed, document)
    else:    
        items = _get_rss_entries(the_feed, document)
    
    document.unlink()
    
    return items

# -----------------------------------------------------------

def format_delicious(item):
        
    d = {
        'url':escape(item.url), 
        'permalink':escape(item.id), 
            
        'title': escape(item.title), 
        #'teaser':item.teaser
    }
    
    return d


import re 

def linkify(text):

    r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
    #r2 = r"((^|\b)www\.([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"

    return re.sub(r1,r'<a href="\1">\1</a>',text)
    
def format_twitter(item):
    
    d = {
        'permalink':escape(item.url), 
            
        'title': linkify(item.title.lstrip('passiomatic:')), 
        #'teaser':item.teaser
    }
        
    return d


def format_blog(item):

    if item.teaser:
        teaser = sanitizer.strip(item.teaser)[:config.TEASER_LEN] + '(&hellip;)'
    else:
        teaser = ''

    d = {
        'permalink': escape(item.url), 
            
        'title': item.title, 
        'teaser': teaser
    }
    
    return d


TEMPLATES = {

    config.DELICIOUS : ("""        
    <li class="clear">
        <h4>Bookmark</h4>
            
        <h3><a href="$url">$title</a>
        </h3>    
         
        <div class="meta">
            $date from <a href="$permalink">$site_name</a>
        </div>    
    </li>
    """, format_delicious),
    
    config.TWITTER : ("""
    <li class="clear">  
        
        <h4>Tweet</h4>
    
        <h3>$title
        </h3>            
        
        <div class="meta">$date from <a href="$permalink">$site_name</a></div>    
    </li>
    """, format_twitter),
    
    config.BLOG : ("""
    <li class="clear">
        
        <h4>Post</h4>
        
        <h3><a href="$permalink">$title &mdash; $teaser</a>
        </h3>
        
        <div class="meta">$date from <a href="$permalink">$site_name</a></div>    
    </li>
    """, format_blog),
}

# -----------------------------------------------------------

from string import Template

#def _u(s): return s.encode('utf-8', 'replace')

#from itertools import cycle
#last_loop = cycle(['', '', '', 'last'])

import urlparse

def get_friendly_name(url):     
    return urlparse.urlsplit(url)[1]
    #return urlparse.urlsplit(url).hostname

def generate_html(items):


    s = ''
    for item in items:
        
        t, fn = TEMPLATES[item.the_feed[0]][0], TEMPLATES[item.the_feed[0]][1]

        s = s + Template(t).safe_substitute(
            
            site_name=escape(get_friendly_name(item.the_feed[1])),
            date=item.date_published.strftime('%b %d, %Y'),

            **fn(item)
                            
            )
        
    return s


if __name__ == "__main__":
    
    items = []
    
    html = ''
    
    for feed in FEEDS:
        items.extend(parse_feed(feed))
            

    items.sort(key=lambda i : i.date_published, reverse=True)
        
    html = generate_html(items[:config.LIMIT]).encode('utf-8', 'replace')
            
    #~ f = open('./_feed_items.html', 'w')
    #~ f.write(html)        
    #~ f.close()
    
    print html
        
        
        

        


    
    

