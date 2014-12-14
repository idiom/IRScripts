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
        response = {'error':''}
        try:
            request = urllib2.build_opener()
            request = urllib2.Request(url)
            request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:27.0) Gecko/20121011 Firefox/27.0')
            response = urllib2.urlopen(request, timeout = 10)
        except urllib2.URLError as e:
            response['error'] = str(e)
        except socket.timeout as e:
            response['error'] = str(e)
        return response
    
    def querydshield(self):
        result = None
        data = ''
        response = self.__sendrequest('https://isc.sans.edu/api/ip/%s?json' % self.ip)
        try:
            data = json.loads(response.read())['ip']
        except AttributeError as e:
            data = response
        return data
        
    def ipinfo(self):
        result = None
        data = ''
        response = self.__sendrequest('http://ipinfo.io/%s/json' % self.ip)
        try:
            data = json.loads(response.read())
        except AttributeError as e:
            data = response
        return data
        
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

def getipinfo(ip,qvt):
    print 'DShield Results'
    data = ip.querydshield()
    print '-'*32 
    for key in data.keys():
        print '  {:15} {:15}'.format(key.capitalize(),data[key])
    print '-'*32  
    print
    
    print 'ipinfo.io Results'
    data = ip.ipinfo()
    print '-'*32 
    for key in data.keys():
        print '  {:15} {:15}'.format(key.capitalize(),data[key])
    print '-'*32  
    print
    
    if qvt:
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
    
    
   
def main():

    parser = argparse.ArgumentParser(description="Query services for information about an IP Address")
    parser.add_argument("ip", help="The target IP address")  
    parser.add_argument('--vt',dest='vt',action='store_true',help="Query VirusTotal") 
    parser.add_argument('--blacklists',dest='blacklists',action='store_true',help="Check if the IP exists in any blacklists") 
    parser.add_argument('--tor',dest='tor',action='store_true',help="Query Tor Services") 
    parser.add_argument('--all',dest='all',action='store_true',help="Query All Services") 
    parser.add_argument('--debug',dest='debug',action='store_true',help="Print debug information")
    args = parser.parse_args()
    
    ip = IPInfo(args.ip)
    print
    
    getipinfo(ip,args.vt)
    
    if args.blacklists or args.all:
        print 'Not Implemented' 
    
    if args.tor or args.all:
        print 'Not Implemented'         
    

if __name__ == '__main__':
    main()
