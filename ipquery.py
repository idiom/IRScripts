#!/usr/bin/env python


'''

    Simple script to query VT for 
    resolutions and detections for an IP
    
'''

import simplejson
import urllib2
import urllib
import argparse
import time

_url = "http://www.virustotal.com/vtapi/v2/ip-address/report"
_apikey = ""

def query_url(args):
    
    if _apikey == "":
        raise Exception("API key is required!")
    parameters = {"ip": args.ip,
               "apikey": _apikey}
    response = urllib.urlopen('%s?%s' % (_url, urllib.urlencode(parameters)))
    
    data = response.read()
    jdata = simplejson.loads(data)
    if jdata["response_code"] == 1:
        if args.all:
            #format and print everthing
            print(simplejson.dumps(jdata, sort_keys=True, indent=4 * ' '))
        else:
            if args.resolutions:
                if "resolutions" in jdata:
                    rdat =  jdata["resolutions"]
                    print
                    print
                    print "Found %d Resolutions" % len(rdat)
                    print "%-24s%s" % ("Date","Hostname")
                    print
                    for res in rdat:
                        print "%-24s%s" % (res["last_resolved"],res["hostname"])
                
                    print
                else:
                    print "No Resolutions Found..."
            
            if args.detectedurls:
                if "detected_urls" in jdata:
                    ddat =  jdata["detected_urls"]
                    print
                    print
                    print "%-11s %-5s %-19s %s" % ("Positives","Total","Date","URL")

                    for res in ddat:
                        print "%-11d %-5d %-19s %s" % (res["positives"],res["total"],res["scan_date"],res["url"],)
                
                    print 
                else:
                    print "No Detections Found..."


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="IP to submit")
    parser.add_argument("-a","--all", help="Return the raw response", action="store_true")
    parser.add_argument("-r","--resolutions", help="Output IP Resolutions", action="store_true")
    parser.add_argument("-d","--detectedurls", help="Output Detected URLs", action="store_true")
    args = parser.parse_args()
    query_url(args)
    
