#!/usr/bin/env python

import urllib
import urllib2
import json
import sys
import sqlite3
import time
from datetime import datetime
import argparse
 
 
def calctime(days,basetime):
    '''
    Calculate the time offset based on the last entry in moz_places. 
    '''
    nbase = datetime.fromtimestamp(basetime/1000000.0)
    bdate = time.mktime(datetime(nbase.year,nbase.month,nbase.day,0,0,0).timetuple())*1000000
    return long(bdate - ((86400 * days) * 1000000))
 
def sitereview(target_url):
    
    #TODO: Figure out query limit and throttle requests. 
    
    url = 'http://sitereview.bluecoat.com/rest/categorization'
    targeturl = {'url' : target_url}
    data = urllib.urlencode(targeturl)                
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    data = json.load(response)                                    
                
    try:                    
        category = data['categorization'].split('>')[1].split('<')[0]                        
        print
        print '==================================='
        print 'URL: %s'         % data['url']
        print 'Category: %s'    % category
        print '==================================='
        
    except Exception as e:
        print 'Error processing %s' % url
        print e                
        time.sleep(10)          
 
def main(target, days,sr):
  
    conn = sqlite3.connect(target)
    c = conn.cursor()    

    c.execute('''SELECT MAX(last_visit_date) FROM moz_places''') 
    basetime = c.fetchone()[0]
    print 'Max Timestamp %d' % basetime
    test = calctime(int(days),basetime)    
    
    c.execute('''SELECT count(1) FROM moz_places where last_visit_date >= %d''' % test)
    print 'Number of Items %d' % c.fetchone()[0]
    
    c.execute('''SELECT moz_places.url, id, 
                        datetime(last_visit_date/1000000, 
                        'unixepoch', 'localtime') 
                        FROM moz_places where last_visit_date >= %d''' % test)
    
    print 'Last Visit\t\tURL'
    for row in c:        
        if row[0].startswith('http'):        
            
            print '%s - %s' % (row[2],row[0])
            if sr:
                sitereview(row[0])
            
    return 0
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to work with the Firefox History")
    parser.add_argument("file", help="The places.sqlite file to process")
    parser.add_argument("days", help="The number of days to process. This is the number of days since the last item in the moz_places table")    
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug messages ")
    parser.add_argument('-s','--sitereview',dest='sitereview',action='store_true',help="Query bluecoat for URL category.")
    parser.add_argument('-e','--exclude',dest='exclude',help="Strings to exclude from any external queries")
    args = parser.parse_args()

    main(args.file, args.days, args.sitereview)
