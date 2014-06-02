#! /usr/bin/python

import argparse 
import urllib2
import urllib
import json
import datetime


def querydshield(ip):
    result = None
    try:
        response = urllib2.urlopen('https://isc.sans.edu/api/ip/%s?json' % ip )
        data = json.loads(response.read())['ip']
        return data
    except:
        return 'An error occured...'

def queryberkley(ip):
    resultset = {'exists':False,'lasttime':''}
    exists = False
    response = urllib2.urlopen('https://security.berkeley.edu/aggressive_ips/ips')
    for line in response:
        if ip in line:
            resultset['exists'] = True
            ldat = line.split(' ')
            resultset['lasttime'] = (datetime.datetime.fromtimestamp(int(ldat[-1])).strftime('%Y-%m-%d'))
            resultset
            break
    return resultset
    
def queryblde(ip):
    #check blocklist.de
    exists = False
    response = urllib2.urlopen('http://lists.blocklist.de/lists/all.txt')
    for line in response:
        if ip in line:
            exists = True
            break
    return exists

def queryashun(ip):
    resultset = {'exists':False,'updated':'','comment':''}
    exists = False
    response = urllib2.urlopen('http://www.autoshun.org/files/shunlist.csv')
    for line in response:
        if ip in line:
            resultset['exists'] = True
            ldat = line.split(',')
            resultset['updated'] = ldat[1]
            resultset['comment'] = ldat[2]
            break
    return resultset
    
def queryethreats(ip):
    exists = False
    response = urllib2.urlopen('http://rules.emergingthreats.net/blockrules/')
    for line in response:
        if ip in line:
            exists = True
            break
    return exists

def querymalcode(ip):
    exists = False
    request = urllib2.build_opener()
    request = urllib2.Request('http://malc0de.com/bl/IP_Blacklist.txt')
    request.add_header('User-Agent','Mozilla/5.0')
    response = urllib2.urlopen(request)
    for line in response:
        if ip in line:
            exists = True
            break
    return exists
    
def queryspamhausbl(ip):
    exists = False
    request = urllib2.build_opener()
    request = urllib2.Request('http://www.spamhaus.org/drop/drop.txt')
    request.add_header('User-Agent','Mozilla/5.0')
    response = urllib2.urlopen(request)
    for line in response:
        if ip in line:
            exists = True
            break
    return exists
   
def main():
    parser = argparse.ArgumentParser(description="Query services for information about an IP Address")
    parser.add_argument("ip", help="The target IP address")    
    parser.add_argument('-d','--debug',dest='debug',action='store_true',help="Print debug information")
    args = parser.parse_args()
    print
    print
    print 'Querying DShield'
    data = querydshield(args.ip)
    print '-'*32 
    for key in data.keys():
        print '  {:15} {:15}'.format(key.capitalize(),data[key])
    print '-'*32  
    print
    print 'Checking Berkley Agressive IPs'
    data = queryberkley(args.ip)
    print '-'*32  
    print '  {:15} {:15}'.format('Identified',str(data['exists']))
    if data['exists']:
        print '  {:15} {:15}'.format('Last Updated',data['lasttime'])
    print '-'*32 
    print
    print 'Checking blocklist.de'
    data = queryblde(args.ip)
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking autoshun'
    data = queryashun(args.ip)
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data['exists']))
    if data['exists']:
        print '  {:15} {:15}'.format('Last Updated',data['updated'])
        print '  {:15} {:15}'.format('Comment',data['comment'])
    print
    print 'Checking Emerging Threats'
    data = queryethreats(args.ip)
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking malc0de'
    data = querymalcode(args.ip)
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32
    print
    print 'Checking spamhaus Blacklist'
    data = queryspamhausbl(args.ip)
    print '-' * 32
    print '  {:15} {:15}'.format('Identified',str(data))
    print '-' * 32

if __name__ == '__main__':
    main()
