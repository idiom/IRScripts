#! /usr/bin/python

import argparse 
import urllib2
import urllib
import json
import datetime


class IPInfo:
    
    def __init__(self,ip):
        self.ip = ip
    
    def __sendrequest(self,url):
        request = urllib2.build_opener()
        request = urllib2.Request(url)
        request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:27.0) Gecko/20121011 Firefox/27.0')
        response = urllib2.urlopen(request)
        return response
    
    def querydshield(self):
        result = None
        try:
            response = self.__sendrequest('https://isc.sans.edu/api/ip/%s?json' % self.ip)
            data = json.loads(response.read())['ip']
            return data
        except:
            return 'An error occured...'

    def queryberkley(self):
        resultset = {'exists':False,'lasttime':''}
        exists = False
        response = self.__sendrequest('https://security.berkeley.edu/aggressive_ips/ips')
        for line in response:
            if self.ip in line:
                resultset['exists'] = True
                ldat = line.split(' ')
                resultset['lasttime'] = (datetime.datetime.fromtimestamp(int(ldat[-1])).strftime('%Y-%m-%d'))
                resultset
                break
        return resultset
        
    def queryblde(self):
        #check blocklist.de
        exists = False
        response = self.__sendrequest('http://lists.blocklist.de/lists/all.txt')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists

    def queryashun(self):
        resultset = {'exists':False,'updated':'','comment':''}
        exists = False
        response = self.__sendrequest('http://www.autoshun.org/files/shunlist.csv')
        for line in response:
            if self.ip in line:
                resultset['exists'] = True
                ldat = line.split(',')
                resultset['updated'] = ldat[1]
                resultset['comment'] = ldat[2]
                break
        return resultset
        
    def queryethreats(self):
        exists = False
        response = self.__sendrequest('http://rules.emergingthreats.net/blockrules/')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists

    def querymalcode(self):
        exists = False
        response = self.__sendrequest('http://malc0de.com/bl/IP_Blacklist.txt')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists
        
    def queryspamhausbl(self):
        exists = False
        response = self.__sendrequest('http://www.spamhaus.org/drop/drop.txt')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists
   
def main():
    
    parser = argparse.ArgumentParser(description="Query services for information about an IP Address")
    parser.add_argument("ip", help="The target IP address")    
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug information")
    args = parser.parse_args()
    
    ip = IPInfo(args.ip)
    
    print
    print
    print 'Querying DShield'
    data = ip.querydshield()
    print '-'*32 
    for key in data.keys():
        print '  {:15} {:15}'.format(key.capitalize(),data[key])
    print '-'*32  
    print
    print 'Checking Berkley Agressive IPs'
    data = ip.queryberkley()
    print '-'*32  
    print '  {:15} {:15}'.format('Identified',str(data['exists']))
    if data['exists']:
        print '  {:15} {:15}'.format('Last Updated',data['lasttime'])
    print '-'*32 
    print
    print 'Checking blocklist.de'
    data = ip.queryblde()
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking autoshun'
    data = ip.queryashun()
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data['exists']))
    if data['exists']:
        print '  {:15} {:15}'.format('Last Updated',data['updated'])
        print '  {:15} {:15}'.format('Comment',data['comment'])
    print
    print 'Checking Emerging Threats'
    data = ip.queryethreats()
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking malc0de'
    data = ip.querymalcode()
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking spamhaus Blacklist'
    data = ip.queryspamhausbl()
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32

if __name__ == '__main__':
    main()
