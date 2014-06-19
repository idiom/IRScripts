#! /usr/bin/python

import argparse 
import urllib2
import urllib
import json
import datetime


class IPInfo:
    VTAPIKEY = '---Your API Key---'

    
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
        
    def querydshieldtopscanners(self):
        exists = False
        response = self.__sendrequest('http://feeds.dshield.org/top10-2.txt')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists
    
    
        
    def queryzeustracker(self):
        exists = False
        response = self.__sendrequest('https://zeustracker.abuse.ch/blocklist.php?download=badips')
        for line in response:
            if self.ip in line:
                exists = True
                break
        return exists
        
    def queryvt(self):
        if IPInfo.VTAPIKEY == '---Your API Key---':
            return {'response_code':0,'verbose_msg':'No API Key'}
        parameters = {'ip': self.ip, 'apikey': IPInfo.VTAPIKEY}
        url = 'https://www.virustotal.com/vtapi/v2/ip-address/report?%s' % urllib.urlencode(parameters)
        response = json.loads(self.__sendrequest(url).read())
        return response
        
class fontcolors:
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    
   
def main():

    parser = argparse.ArgumentParser(description="Query services for information about an IP Address")
    parser.add_argument("ip", help="The target IP address")  
    parser.add_argument('--info',dest='info',action='store_true',help="Query Services for information on the IP") 
    parser.add_argument('--blacklists',dest='blacklists',action='store_true',help="Check if the IP exists in any blacklists") 
    parser.add_argument('--all',dest='all',action='store_true',help="Query All Services") 
    parser.add_argument('--ds',dest='ds',action='store_true',help="Query DShield for Info on IP")
    parser.add_argument('--dsts',dest='dsts',action='store_true',help="Query DShield Top Scanners")     
    parser.add_argument('--brk',dest='brk',action='store_true',help="Query Berkley Agressive IPs") 
    parser.add_argument('--bld',dest='bld',action='store_true',help="Query Blocklist.de") 
    parser.add_argument('--ashun',dest='ashun',action='store_true',help="Query Autoshun") 
    parser.add_argument('--ethreat',dest='ethreat',action='store_true',help="Query Emerging Threats") 
    parser.add_argument('--mc',dest='mc',action='store_true',help="Query malc0de DB") 
    parser.add_argument('--sh',dest='sh',action='store_true',help="Query Spamhaus Blacklist") 
    parser.add_argument('--zs',dest='zs',action='store_true',help="Query Zeus Tracker Blacklist") 
    parser.add_argument('--vt',dest='vt',action='store_true',help="Query VirusTotal. Requires Public API Key")  
    parser.add_argument('--debug',dest='debug',action='store_true',help="Print debug information")
    args = parser.parse_args()
    
    ip = IPInfo(args.ip)
    print
    print
    if args.ds or args.info or args.all:
        print 'Querying DShield'
        data = ip.querydshield()
        print '-'*32 
        for key in data.keys():
            print '  {:15} {:15}'.format(key.capitalize(),data[key])
        print '-'*32  
        print
        
    if args.vt or args.info or args.all:
        print 'Checking VirusTotal'
        data = ip.queryvt()
        print '-' * 32
        if data['response_code'] == 0:
            print '  {:15} {:15}'.format('Found?','False')
            print '  {:15} {:15}'.format('Message',data['verbose_msg'])
        else:
            print '  {:15} {:15}'.format('Found?','True')
            print 
            print '  {:20} {:20}'.format('Last Resolved','Hostname')
            
            for res in data['resolutions']:
                print '  {:20} {:20}'.format(res['last_resolved'],res['hostname'])
        print '-' * 32
        print
        print 'Latest detected URLs'
        print

        if "detected_urls" in data:
            ddat =  data["detected_urls"]
            print
            print '  {:10} {:5} {:^19} {:^30}'.format('Positives','Total','Date','URL')
            for res in ddat:
                print '  {:^10} {:^5} {:19} {:30}'.format(res["positives"],res["total"],res["scan_date"],res["url"])
        
            print 
        else:
            print "No Detections Found..."
        print '-' * 32
    
    if args.brk or args.blacklists or args.all:
        print 'Checking Berkley Agressive IPs'
        data = ip.queryberkley()
        print '-'*32  
        print '  {:15} {:15}'.format('Found?',str(data['exists']))
        if data['exists']:
            print '  {:15} {:15}'.format('Last Updated',data['lasttime'])
        print '-'*32 
        print
    
    if args.bld or args.blacklists or args.all:
        print 'Checking blocklist.de'
        data = ip.queryblde()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
    
    if args.ashun or args.blacklists or args.all:
        print 'Checking autoshun'
        data = ip.queryashun()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data['exists']))
        if data['exists']:
            print '  {:15} {:15}'.format('Last Updated',data['updated'])
            print '  {:15} {:15}'.format('Comment',data['comment'])
        print
    
    if args.ethreat or args.blacklists or args.all:
        print 'Checking Emerging Threats'
        data = ip.queryethreats()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
    
    if args.mc or args.blacklists or args.all:
        print 'Checking malc0de'
        data = ip.querymalcode()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
    
    if args.sh or args.blacklists or args.all:
        print 'Checking spamhaus Blacklist'
        data = ip.queryspamhausbl()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
    
    if args.sh or args.blacklists or args.all:
        print 'Checking Zeus Tracker Blacklist'
        data = ip.queryzeustracker()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
        
    if args.dsts or args.blacklists or args.all:
        print 'Checking DShield Top Scanners'
        data = ip.querydshieldtopscanners()
        print '-' * 32
        print '  {:15} {:15}'.format('Found?',str(data))
        print '-' * 32
        print
        
    

if __name__ == '__main__':
    main()
