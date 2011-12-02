import urlparse
from string import Template
from cgi import escape
from xml.dom import minidom
import urllib2 
import time
from datetime import datetime

from . import Item

USER_AGENT = 'Passiomatic Feedhub/0.5.1 <http://lab.passiomatic.com/feedhub/>'

class Feed(object):

    def __init__(self,url,site_name,css_class=None):
        self.site_name = site_name
        self.css_class = css_class or 'post'
        self.url = url
        self.TEMPLATE = '''
            <li class="clear $css_class">
                <h3><a href="$url">$title</a></h3>
                <p>$content</p>
                <div class="meta">$date from <a href="$url">$site_name</a></div>
            </li>
        '''

    def _get_feed(self):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', USER_AGENT)]
        request = opener.open(self.url)
        data = request.read()
        request.close()
        return data


    def _get_items(self,document ):
        items = []
        for entry in document.getElementsByTagName('entry'):
            item = self._get_item_details(entry)
            item.the_feed = self
            items.append(item)
        for entry in document.getElementsByTagName('item'):
            item = self._get_item_details(entry)
            item.the_feed = self
            items.append(item)
        return items

    def _get_item_details(self,entry):
        item = Item()

        try:
            item.url = entry.getElementsByTagName('link')[0].getAttribute('href')
        except IndexError:
            item.url = entry.getElementsByTagName('link')[0].firstChild.nodeValue

        if item.url == '':
            try:
                item.url = entry.getElementsByTagName('id')[0].firstChild.nodeValue
            except IndexError:
                item.url = entry.getElementsByTagName('guid')[0].firstChild.nodeValue

        try:
            item.title = entry.getElementsByTagName('title')[0].firstChild.nodeValue
        except AttributeError:
            item.title = ''

        try:
            item.content = entry.getElementsByTagName('content')[0].firstChild.nodeValue
        except IndexError:
            try:
                item.content = entry.getElementsByTagName('summary')[0].firstChild.nodeValue
            except IndexError:
                try:
                    item.content = entry.getElementsByTagName('description')[0].firstChild.nodeValue
                except IndexError:
                    item.content = ''

        try:
            date_published = entry.getElementsByTagName('published')[0].firstChild.nodeValue
        except IndexError:
            try:
                date_published = entry.getElementsByTagName('pubDate')[0].firstChild.nodeValue
            except IndexError:
                date_published = entry.getElementsByTagName('updated')[0].firstChild.nodeValue

        # get date
        try:
            # 2008-10-27T11:06:52 (ignore time zone)
            date_published = datetime(*(time.strptime(date_published[:19], '%Y-%m-%dT%H:%M:%S')[0:6]))
        except ValueError:
            try:
                # Sun, 08 Feb 2009 22:48:25 (ignore time zone)
                date_published = datetime(*(time.strptime(date_published[:25], '%a, %d %b %Y %H:%M:%S')[0:6]))
            except ValueError:
                date_published = datetime.now()

        item.date_published = date_published

        return item


    def parse_feed(self):
        try:
            s = self._get_feed()
        except urllib2.URLError:
            return []

        document = minidom.parseString(s)
        items = self._get_items(document)
        document.unlink()

        return items


    def _format(self,item):
        d = {
                'css_class': self.css_class,
                'url':escape(item.url), 
                'title': escape(item.title), 
                'content':item.content
        }
        return d


    def render_item_html(self,item):
        return  Template(self.TEMPLATE).safe_substitute(
                site_name=escape(self.site_name),
                date=item.date_published.strftime('%b %d, %Y'),
                **self._format(item)
                )

