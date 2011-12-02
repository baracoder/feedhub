# -*- coding: utf-8 -*-

try:
    import config
    FEEDS = config.FEEDS
except ImportError:
    print "Unable to find file config.py. Please rename config-sample.py first."
    import sys; sys.exit(1)

# -----------------------------------------------------------

#def _u(s): return s.encode('utf-8', 'replace')

#from itertools import cycle
#last_loop = cycle(['', '', '', 'last'])


def generate_html(items):
    s = ''
    for item in items:
        s = s + item.the_feed.render_item_html(item)

    return s


if __name__ == "__main__":
    items = []
    for feed in FEEDS:
        items.extend(feed.parse_feed())
    items.sort(key=lambda i : i.date_published, reverse=True)

    html = generate_html(items[:config.LIMIT]).encode('utf-8', 'replace')
    print html

