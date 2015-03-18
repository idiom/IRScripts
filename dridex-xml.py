#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import base64
import zlib
import sys
import os.path

'''

Extract compressed Dridex document from xml file. 

'''


def extract_data(filename):
    try:
        print 'Processing File: %s' % filename
        dat = open(filename,'r').read()
        soup = BeautifulSoup(dat)
        print '  Finding bindata section'
        bindat = base64.b64decode(soup.findAll("w:bindata")[0].contents[0])        
       
        print '  Finding compressed doc'
        start = bindat.find('\x78\x9c')
        end   = bindat.find('\x00\x00\x0d')
        if start < 0 or end < 0:
            print 'Error! Compressed section not found...'
            sys.exit(-1)
        print '  Detected compressed file [%d:%d]' % (start, end)
        cdoc = bindat[start:end]
        print '  Extracting compressed doc'        
        payload = zlib.decompress(cdoc)
        of = open('%s-extracted','wb')
        of.write(payload)
        of.close()
        print '...done'
    except Exception as e:
        print 'Something went wrong extracting the doc'
        print e
    

def main(targetfile):
    if os.path.exists(targetfile):
        extract_data(targetfile)
    else:
        sys.exit("Error: File %s doesn't exist" % targetfile)
    return 0

if __name__ == '__main__':
    
    main(sys.argv[1])

