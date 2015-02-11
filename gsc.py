#!/usr/bin/env python


'''
    
    In order to query the google  safebrowse API you need to register for an API key
    using the Google Developer dashboard. 
    
    https://developers.google.com/safe-browsing/key_signup?csw=1

'''

import argparse
import urllib2
import urllib
import socket
import sys

class GSBQuery:

    _APIKEY = ''

    def __init__(self):
        self.result = ''
        pass

    def __sendrequest(self,url):
        response = {'error':''}
        try:
            request = urllib2.Request(url)
            qr = urllib2.urlopen(request, timeout = 10)               
            #TODO: Handle other HTTP Codes Properly  
            if qr.getcode() == 200:
                response['result'] = qr.read()
            elif qr.getcode() == 204:
                response['result'] = 'Not Found'                            
            else:
                response['result'] = 'Unknown: %d' % qr.getcode()
        except urllib2.URLError as e:
            response['error'] = str(e)
        except socket.timeout as e:
            response['error'] = str(e)
        return response

    def dispatch(self, url):
        
        sburl = 'https://sb-ssl.google.com/safebrowsing/api/lookup?client=api&apikey=%s&appver=1.0&pver=3.0&url=%s' % (GSBQuery._APIKEY, url)
        r = self.__sendrequest(sburl)

        self.result = r

    def status(self,key=''):
        return ''

    def report(self,key=''):
        report = ''
        try:
            report = self.result['result']
        except KeyError:
            report = self.result['error']
        return report         



def main():    
    parser = argparse.ArgumentParser(description="Query Google Safebrowse for status of URL (malware/phishing)")
    parser.add_argument("url", help="The target URL")    
    args = parser.parse_args()
    
    print ' Querying for ranking of: %s' % args.url
    gq =GSBQuery()
    gq.dispatch(args.url)
    print ' Result: %s' % gq.report()
    return

if __name__ == '__main__':
    main()

    
