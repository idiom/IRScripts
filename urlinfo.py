#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib
import urllib2
import json
import time
import argparse
 
class URLInfo:
    
    
    
    def __init__(self, debug = False):
        self.debug = debug
        
        
    def sitereview(self,target):
        
        #TODO: Figure out query limit and throttle requests.
        sitedata = {}
        sitedata['error'] = False 
        try:
            
            url = 'http://sitereview.bluecoat.com/rest/categorization'
            targeturl = {'url' : target}
            data = urllib.urlencode(targeturl)                
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            data = json.load(response)                                  
            
            sitedata['category'] = data['categorization'].split('>')[1].split('<')[0]
            sitedata['url'] = data['url']
            sitedata['locked'] = data['locked']
            sitedata['linkable'] = data['linkable']
            sitedata['unrated'] = data['unrated']
            if not sitedata['unrated']:
                sitedata['ratedate'] = data['ratedate'].split(':')[1].split('<img')[0].strip()
            else:
                sitedata['ratedate'] = ''
                
        except Exception as e:
            print e
            sitedata['error'] = True
            sitedata['errordetails'] = e
        finally:
            return sitedata
            
    def vtsearch(self,target):
        print 'Searching VT for entries' 
        
    def urlquery(self,target):
        print 'Searching urlquery for entries' 
 

def main():
    parser = argparse.ArgumentParser(description="A script to show info about a url/domain.")
    parser.add_argument("url", help="The url to get info on.")
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug messages ")
    parser.add_argument('-s','--sitereview',dest='sitereview',action='store_true',help="Query bluecoat for URL category.")
    parser.add_argument('-a','--all',dest='sitereview',action='store_true',help="Query all of the services.")


    args = parser.parse_args()
    urlq = URLInfo()
    if args.sitereview:
        sitedata = urlq.sitereview(args.url)
        if sitedata['error']:
            print 'An error occured querying the service...'
            print sitedata['errordetails']
        else:
            print
            print '==================================='
            print
            print 'URL:       %s' % sitedata['url']
            print 'Category:  %s' % sitedata['category']
            print 'Rate Date: %s' % sitedata['ratedate']
            print 'Unrated:   %s' % sitedata['unrated']
            print
            print '==================================='
 
if __name__ == '__main__':
    main()
