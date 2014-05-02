#!/usr/bin/env python

import urllib
import urllib2
import json
import sys
import sqlite3
import time
from datetime import datetime
import argparse
import os.path
 
 
 
class FFHistory:
    
    def __init__(self, filename):
        
        self.hfile         = None
        self.dbcon         = None 
        self.cursor        = None
        self.lasturl       = None
        self.lasturltime   = None
        self.urlcount      = None
        self.lastvisittime = None

        if  os.path.isfile(filename):
            self.dbcon = sqlite3.connect(filename)
            self.cursor = self.dbcon.cursor()
            self.processfile()
        else:
            raise Exception('File doesn\'t exist...')
    
    
    def processfile(self):
        #Get total URL Count
        self.cursor.execute('''SELECT count(1) FROM moz_places''')
        self.urlcount = self.cursor.fetchone()[0]
        
        #Get Latest timestamp
        self.cursor.execute('''SELECT MAX(last_visit_date) FROM moz_places''')
        self.lastvisittime = self.cursor.fetchone()[0]
        
    def gethistory(self,days):
        ctime = self.calctime(days)
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
        nbase = datetime.fromtimestamp(self.lastvisittime/1000000.0)
        bdate = time.mktime(datetime(nbase.year,nbase.month,nbase.day,0,0,0).timetuple())*1000000
        return (bdate - ((86400 * int(days)) * 1000000))
 
def sitereview(target_url):
    
    #TODO: Figure out query limit and throttle requests. 
    url = 'http://sitereview.bluecoat.com/rest/categorization'
    targeturl = {'url' : target_url}
    data = urllib.urlencode(targeturl)                
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    data = json.load(response) 
    
    #Don't hammer the service
    time.sleep(1)                                   
                
    try:  
        #TODO return a tuple of usefull fields
        category = data['categorization'].split('>')[1].split('<')[0]  
        return category                      
    except Exception as e:
        return e                
 
 

def main():
    parser = argparse.ArgumentParser(description="A script to work with the Firefox History")
    parser.add_argument("file", help="The places.sqlite file to process")
    parser.add_argument("days", help="The number of days to process. This is the number of days since the last item in the moz_places table")    
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug messages ")
    parser.add_argument('-s','--sitereview',dest='sitereview',action='store_true',help="Query bluecoat for URL category.")
    parser.add_argument('-e','--exclude',dest='exclude',help="Strings to exclude from any external queries")
    args = parser.parse_args()

    ffh = FFHistory(args.file)
    urls = ffh.gethistory(args.days)
    for url in urls:
        if args.sitereview:
            print
            print '==================================='
            print 'Date: %s'         % url[0]
            print 'URL: %s'         % url[1]
            print 'Category: %s'    % sitereview(url[1])
            print '==================================='
        else:
            print '%s - %s' % (url[0],url[1])
 
if __name__ == '__main__':
    main()
