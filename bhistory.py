#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib
import urllib2
import json
import sys
import sqlite3
import time
from datetime import datetime
import argparse
import os.path
 
 
 
class BHistory:
    
    browser = {
    0x0: "Chrome",
    0x1: "Firefox"
    }
        
    def __init__(self, filename,debug):
        
        self.hfile         = None
        self.dbcon         = None 
        self.cursor        = None
        self.lasturl       = None
        self.lasturltime   = None
        self.urlcount      = None
        self.lastvisittime = None
        self.browsertype   = None
        self.debug         = debug
        
        self.history_tablename = 'moz_places'

        if  os.path.isfile(filename):
            self.dbcon = sqlite3.connect(filename)
            self.cursor = self.dbcon.cursor()
            self.processfile()
        else:
            raise Exception('File doesn\'t exist...')
            
        
    def processfile(self):
        visit_column = None
        history_tablename = None
        
        #Get Browser Type
        self.cursor.execute('''SELECT count(1) FROM sqlite_master WHERE type='table' AND name='moz_places' ''')
        self.browsertype = self.cursor.fetchone()[0]
        print 'Detected DB as %s' % self.browser[self.browsertype]


        if self.browsertype == 0:
            visit_column = "last_visit_time"
            history_tablename = 'urls'
        else:
            visit_column = "last_visit_date"
            history_tablename = 'moz_places'

        #Get total URL Count
        self.cursor.execute('''SELECT count(1) FROM %s''' % history_tablename)
        self.urlcount = self.cursor.fetchone()[0]
        
        #Get Latest timestamp
        self.cursor.execute('''SELECT MAX(%s) FROM %s ''' % (visit_column,history_tablename))
        self.lastvisittime = self.cursor.fetchone()[0]
        
        #if self.browsertype == 0:
        #    self.lastvisittime = self.lastvisittime - 11644473600000000
        
    def gethistory(self,days):
        ctime = self.calctime(days)
        #chrome query
        #SELECT url,datetime(((last_visit_time-11644473600000000)/1000000),'unixepoch','localtime') as last_visit_time FROM urls
        if self.browsertype == 0:            
            self.cursor.execute('''SELECT url, id, datetime(((last_visit_time-11644473600000000)/1000000),'unixepoch','localtime') as last_visit_time
                            FROM urls where last_visit_time >= %d''' % ctime)
        urls = []
        for row in self.cursor:        
            if row[0].startswith('http'):
                url = row[2],row[0]
                urls.append(url)
        return urls
        
    def calctime(self,days):
        
        '''
        Calculate the time offset based on the last entry in moz_places. 
        '''
        nbase = datetime.fromtimestamp(self.lastvisittime/1000000.0)
        bdate = time.mktime(datetime(nbase.year,nbase.month,nbase.day,0,0,0).timetuple())*1000000
        return (bdate - ((86400 * int(days)) * 1000000))
 
    def sitereview(self,target_url):
        
        #TODO: Figure out query limit and throttle requests. 
        try:
            url = 'http://sitereview.bluecoat.com/rest/categorization'
            targeturl = {'url' : target_url}
            data = urllib.urlencode(targeturl)                
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            data = json.load(response) 

            #Don't hammer the service
            time.sleep(1)                                   
            
            sitedata = {}
          
            sitedata['category'] = data['categorization'].split('>')[1].split('<')[0]
            sitedata['locked'] = data['locked']
            sitedata['linkable'] = data['linkable']
            sitedata['unrated'] = data['unrated']
            if not sitedata['unrated']:
                sitedata['ratedate'] = data['ratedate'].split(':')[1].split('<img')[0].strip()
            else:
                sitedata['ratedate'] = ''
                
        except Exception as e:
            category = e                
        finally:
            return sitedata
 

def main():
    parser = argparse.ArgumentParser(description="A script to work with the Firefox History")
    parser.add_argument("file", help="The places.sqlite file to process")
    parser.add_argument("days", help="The number of days to process. This is the number of days since the last item in the moz_places table")    
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug messages ")
    parser.add_argument('-s','--sitereview',dest='sitereview',action='store_true',help="Query bluecoat for URL category.")
    parser.add_argument('-e','--exclude',dest='exclude',help="Strings to exclude from any external queries")
    args = parser.parse_args()

    ffh = BHistory(args.file,args.debug)
    urls = ffh.gethistory(args.days)
    for url in urls:
        if args.sitereview:
            sitedata = ffh.sitereview(url[1])
            print
            print '==================================='
            print
            print 'Date:      %s' % url[0]
            print 'URL:       %s' % url[1]
            print 'Category:  %s' % sitedata['category']
            print 'Rate Date: %s' % sitedata['ratedate']
            print 'Unrated:   %s' % sitedata['unrated']
            print
            print '==================================='
        else:
            print '%s - %s' % (url[0],url[1])
 
if __name__ == '__main__':
    main()
