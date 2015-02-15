#!/usr/bin/env python


'''

    Query FortiGuard IP Reputation and Blacklist

'''

import argparse
import urllib2
import urllib
import sys
import re

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
        result = {}
        result['Error'] = None
        request = urllib2.Request(url, headers={'User-Agent': self._UserAgent})
        qr = urllib2.urlopen(request, timeout=10)
        try:
            self._represult = qr.read()
            soup = BeautifulSoup(self._represult)
            test = soup.find_all(class_='graph_inner')

            # Loop through the data sections
            for x in range(0, len(test)):
                # Check the Section names
                if test[x].h2.string.startswith('WF Rating History'):
                    result['Rating_History'] = {}
                    rows = test[x].find_all('tr')
                    ratings = []
                    for row_data in rows:
                        cells = row_data.find_all('td')
                        ratings.append((cells[0].string, cells[1].string))
                    result['Rating_History'] = ratings
                elif test[x].h2.string.startswith('IP'):
                    result['IP_Info'] = {}
                    rows = test[x].find_all('tr')
                    iplist = []
                    for row_data in rows:
                        cells = row_data.find_all('td')
                        for cell in cells:
                            ips = cell.find_all('a')
                            for ip in ips:
                                iplist.append(ip.string)
                    result['IP_Info'] = iplist
                elif test[x].h2.string.startswith('Shares the domain'):
                    result['Shared_Domains'] = {}
                    rows = test[x].find_all('tr')
                    domlist = []
                    for row_data in rows:
                        cells = row_data.find_all('td')
                        for cell in cells:
                            hosts = cell.find_all('a')
                            for host in hosts:
                                domlist.append(host.string)
                    result['Shared_Domains'] = domlist

            result['Category'] = soup.h3.string.split(':')[1].lstrip(' ')
        except urllib2.URLError as e:
            if e.code == 400:
                result['Error'] = 'Error: Bad Request'
            elif qr.getcode() == 403:
                result['Error'] = 'Error: Invalid ClientId'
            elif qr.getcode() == 503:
                result['Error'] = 'Error: Service Unavailable!'
        return result

def print_reputation(rep):
    rep_data = '\nReputation Data\n'
    rep_data += ' {:20}{:64}\n'.format('Category:', rep['Category'])

    if 'Rating_History' in rep:
        rep_data += ' {:20}{:64}\n'.format('Rating History:', '')
        for rating in rep['Rating_History']:
            rep_data += ' {:20}{:64}\n'.format('', '%s - %s' % (rating[0], rating[1]))
    else:
        rep_data += ' {:20}{:64}\n'.format('Rating History:', 'Unknown')

    if 'IP_Info' in rep:
        rep_data += ' {:20}{:64}\n'.format('IP Info:', '')
        for ip in rep['IP_Info']:
            rep_data += ' {:20}{:64}\n'.format('', ip)
    else:
        rep_data += ' {:20}{:64}\n'.format('IP Info:', 'Unknown')

    if 'Shared_Domains' in rep:
        rep_data += ' {:20}{:64}\n'.format('Shared Domains:', '')
        for host in rep['Shared_Domains']:
            rep_data += ' {:20}{:64}\n'.format('', host)
    else:
        rep_data += ' {:20}{:64}\n'.format('Shared Domains:', 'Unknown')

    print rep_data


def main():
    parser = argparse.ArgumentParser(description="Query FortiGuard Reputation and Blacklist")
    parser.add_argument("url", help="The target URL or IP")
    parser.add_argument('-b', '--blacklist', dest='blacklist', action='store_true', help="Query Blacklist")
    parser.add_argument('-r', '--rep', dest='rep', action='store_true', help="Query Reputation")
    args = parser.parse_args()
    print '\n Querying for: %s' % args.url
    fgl = FGLookup()

    if args.blacklist:
        print ' Blacklist: %s' % fgl.check_blacklist(args.url)
    elif args.rep:
        print_reputation(fgl.check_reputation(args.url))
    else:
        print ' Blacklist: %s' % fgl.check_blacklist(args.url)
        print_reputation(fgl.check_reputation(args.url))
    print ''



if __name__ == '__main__':
    main()
