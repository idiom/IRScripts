#!/usr/bin/env python
# -*- coding: utf8 -*-

__description__ = 'Script to work with Chrome or Firefox browser history.'
__author__ = 'Sean Wilson'
__version__ = '0.0.2'

import urllib
import urllib2
import json
import sys
import sqlite3
import time
from datetime import datetime
import argparse
import os.path
import re
 
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
            print 'Total URLs Detected: %d' % self.urlcount
            print 'Last Visit: %s' % self.lastvisittime
            if self.nvtcount > 0:
                print 'Warning! A number of records were detected with no timestamp.'
                print 'with no timestamp: %d' % self.nvtcount
        else:
            raise Exception('File doesn\'t exist...')
            
    def processfile(self):
        visit_column = None
        history_tablename = None
        
        print 'Processing File....'
        
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
        
        #Get count of records with a null timestamp
        self.cursor.execute('''SELECT count(1) FROM %s WHERE %s IS NULL ''' % (history_tablename,visit_column))
        self.nvtcount = self.cursor.fetchone()[0]
        
    def gethistory(self,days):
        ctime = self.calctime(days)

        if self.browsertype == 0:            
            self.cursor.execute('''SELECT url, id, datetime(((last_visit_time/1000000)-11644473600),'unixepoch','localtime') 
                                as last_visit_time
                                FROM urls where ((last_visit_time/1000000)-11644473600) >= %d''' % ctime)
        else:

            self.cursor.execute('''SELECT moz_places.url, id, 
                            datetime(last_visit_date/1000000, 
                            'unixepoch', 'localtime') 
                            FROM moz_places where last_visit_date >= %d''' % ctime)

        
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
        
        if self.browsertype == 0x0:            
            nbase = datetime.fromtimestamp(((self.lastvisittime/1000000)-11644473600))
            bdate = time.mktime(datetime(nbase.year,nbase.month,nbase.day,0,0,0).timetuple())                                    
            return (bdate - (86400 * int(days)))
        else:
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

            # Don't hammer the service
            time.sleep(1)                                   
            
            sitedata = {}
            
            if 'errorType' in data:                
                sitedata = data
            else:                
                sitedata['category'] = data['categorization'].split('>')[1].split('<')[0]
                sitedata['locked'] = data['locked']
                sitedata['linkable'] = data['linkable']
                sitedata['unrated'] = data['unrated']
                sitedata['ratedate'] = 'Unknown'
            
                if not sitedata['unrated'] and data['ratedate']:                
                    sitedata['ratedate'] = data['ratedate'].split(':')[1].split('<img')[0].strip()                                
        except Exception as e:
            sitedata['errorType'] = e                
            sitedata['error'] = 'Property Error'     
        finally:
            return sitedata
 

def main():
    parser = argparse.ArgumentParser(description="A script to work with the Firefox History")
    parser.add_argument("file", help="The places.sqlite file to process")
    parser.add_argument("days", help="The number of days to process. This is the number of days since the last item in the moz_places table")    
    parser.add_argument('--debug',dest='debug', action='store_true', help="Print debug messages ")
    parser.add_argument('-s','--sitereview', dest='sitereview',action='store_true', help="Query bluecoat for URL category.")
    parser.add_argument('-e','--exclude', dest='exclude', help="Exclude urls using hte supplied regex")
    args = parser.parse_args()

    ffh = BHistory(args.file,args.debug)
    urls = ffh.gethistory(args.days)
    
    if args.exclude:
        exreg = re.compile(args.exclude)
    
    for url in urls:
        if args.exclude:
            if exreg.match(url[1]):            
                continue
        if args.sitereview:        
            sitedata = ffh.sitereview(url[1])            

            print
            print '==================================='
            print ' {:<12} {}'.format("Date:",url[0])
            print ' {:<12} {}'.format("URL:",url[1])
            
            if 'errorType' in sitedata:
                print ' {:<12} {}'.format('ErrorType:', sitedata['errorType'])
                print ' {:<12} {}'.format('Error:', sitedata['error'])
                if sitedata['errorType'] == 'intrusion':
                    break                                                    
            else:                    
                print                    
                print ' {:<12} {}'.format('Category:', sitedata['category'])
                print ' {:<12} {}'.format('Rate Date:', sitedata['ratedate'])
                print ' {:<12} {}'.format('Unrated:', sitedata['unrated'])
                print
                print '==================================='
            
        else:
            print '%s - %s' % (url[0],url[1])
 
if __name__ == '__main__':
    main()
