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
        response = {'error':'', 'result':''}
        try:
            request = urllib2.Request(url)
            qr = urllib2.urlopen(request, timeout = 10)                           
            if qr.getcode() == 200:
                response['result'] = qr.read()
            elif qr.getcode() == 204:
                response['result'] = 'URL Not Found (OK)'                           
            else:
                response['result'] = 'Unknown: %d' % qr.getcode()
        except urllib2.URLError as e:            
            if e.code == 400:
                response['error'] = 'Bad Request: The HTTP request was not correctly formed. [Check APIKey]'
            elif qr.getcode() == 403:
                response['error'] = 'Invalid ClientId'
            elif qr.getcode() == 503:
                response['result'] = 'Service Unavailable!'
            elif qr.getcode() == 505:
                response['result'] = 'HTTP Version not supported'
            else:
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
        if self.result['result'] == '':
            report = self.result['error']
        else:
            report = self.result['result']
        return report         



def main():    
    parser = argparse.ArgumentParser(description="Query Google Safebrowse for status of URL (malware/phishing)")
    parser.add_argument("url", help="The target URL")    
    args = parser.parse_args()
    print '\n Querying for ranking of: %s' % args.url
    gq =GSBQuery()
    gq.dispatch(args.url)
    print ' Result: %s\n' % gq.report()
    
    return

if __name__ == '__main__':
    main()

    
