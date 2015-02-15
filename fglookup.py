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

    _UserAgent = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
    _represult = None
    _blresult  = None

    def __init__(self, agent=None):

        if agent is not None:
            self._UserAgent = agent


    def check_blacklist(self, target):
        """

        Check if the <target> is in the FortiGuard blacklist.

        The target can be an IP address or URL.

        """

        url = "http://www.nospammer.net/web/spam_lookup.php"
        result = ''

        reqdata = urllib.urlencode({'signature': target})
        request = urllib2.Request(url, reqdata, headers={'User-Agent': self._UserAgent})

        qr = urllib2.urlopen(request, timeout=10)

        try:
            self._blresult = qr.read()
            soup = BeautifulSoup(self._blresult)
            dat = soup.select("tr style")

            # The dom is screwy so we need to manually parse out the result.
            # Or more likely I just need to RTFM the soup docs
            block = str(dat[0])
            tl = block.find(target)
            result = block[tl:].split('<')[0].replace('\"', '')
        except urllib2.URLError as e:
            if e.code == 400:
                result = 'Error: Bad Request'
            elif qr.getcode() == 403:
                result = 'Error: Invalid ClientId'
            elif qr.getcode() == 503:
                result = 'Error: Service Unavailable!'

        return result



    def check_reputation(self, target):
        url = 'http://www.fortiguard.com/ip_rep/?data=%s&lookup=lookup' % target
        result = ''
        request = urllib2.Request(url, headers={'User-Agent': self._UserAgent})
        qr = urllib2.urlopen(request, timeout=10)
        try:
            self._represult = qr.read()
            soup = BeautifulSoup(self._represult)
            result = soup.h3.string
        except urllib2.URLError as e:
            if e.code == 400:
                result = 'Error: Bad Request'
            elif qr.getcode() == 403:
                result = 'Error: Invalid ClientId'
            elif qr.getcode() == 503:
                result = 'Error: Service Unavailable!'

        return result

def main():
    parser = argparse.ArgumentParser(description="Query FortiGuard Reputation and Blacklist")
    parser.add_argument("url", help="The target URL or IP")
    parser.add_argument('-b', '--blacklist', dest='blacklist', action='store_true', help="Query Blacklist")
    parser.add_argument('-r', '--rep', dest='rep', action='store_true', help="Query Reputation")
    args = parser.parse_args()
    print '\n Checking: %s' % args.url
    fgl = FGLookup()

    if args.blacklist:
        print ' Blacklist: %s' % fgl.check_blacklist(args.url)
    elif args.rep:
        print ' %s' % fgl.check_reputation(args.url)
    else:
        print ' Blacklist: %s' % fgl.check_blacklist(args.url)
        print ' %s' % fgl.check_reputation(args.url)
    print ''

if __name__ == '__main__':
    main()
