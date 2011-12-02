from default import Feed

class TwitterFeed(Feed):
    def __init__(self,userid):
        self.site_name = 'twitter'
        self.css_class = 'twitter'
        self.url = 'http://twitter.com/statuses/user_timeline/'+userid+'.rss'
        self.TEMPLATE = '''
            <li class="clear $css_class">
                <h3><a href="$url">$title</a></h3>
                <div class="meta">$date from <a href="$url">$site_name</a></div>
            </li>
        '''
