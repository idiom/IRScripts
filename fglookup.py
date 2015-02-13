#!/usr/bin/env python


'''

    Query FortiGuard IP Reputation and Blacklist

'''

import argparse
import urllib2
import urllib
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit('Error - Please ensure you install the beautifulsoup4 library (pip install beautifulsoup4)')


class FGLookup:

    def __init__(self):
        pass

    def check_blacklist(self, target):
        url = "http://www.nospammer.net/web/spam_lookup.php"
        values = {'signature': target}
        reqdata = urllib.urlencode(values)
        request = urllib2.Request(url, reqdata)
        qr = urllib2.urlopen(request, timeout=10)

        if qr.getcode() == 200:
            soup = BeautifulSoup(qr.read())
            dat = soup.select("tr style")

            # The dom is screwy so we need to manually parse out the result.
            # Or more likely I just need to RTFM the soup docs
            block = str(dat[0])
            tl = block.find(target)
            return block[tl:].split('<')[0].replace('\"', '')
        else:
            return 'Error: No Result'

    def check_reputation(self, target):
        url = 'http://www.fortiguard.com/ip_rep/?data=%s&lookup=lookup' % target
        request = urllib2.Request(url)
        qr = urllib2.urlopen(request, timeout=10)

        if qr.getcode() == 200:
            soup = BeautifulSoup(qr.read())
            return soup.h3.string
        else:
            return 'Error: No Result'

def main():
    parser = argparse.ArgumentParser(description="Query FortiGuard Reputation and Blacklist")
    parser.add_argument("url", help="The target URL or IP")
    parser.add_argument('-b', '--blacklist', dest='blacklist', action='store_true', help="Query Blacklist")
    parser.add_argument('-r', '--rep', dest='rep', action='store_true', help="Query Reputation")
    args = parser.parse_args()
    print '\n Checking: %s' % args.url
    fgl = FGLookup()

    if args.blacklist:
        print ' %s' % fgl.check_blacklist(args.url)
    elif args.rep:
        fgl.check_reputation(args.url)
    else:
        print ' %s' % fgl.check_blacklist(args.url)
        print ' %s' % fgl.check_reputation(args.url)

if __name__ == '__main__':
    main()
