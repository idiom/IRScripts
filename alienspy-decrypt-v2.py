__description__ = 'AlienSpy Decoder v2'
__author__ = 'Sean Wilson'
__version__ = '0.0.1'
__date__ = '2015/03/18'


import hashlib
from StringIO import StringIO
import zipfile
import argparse
from Crypto.Cipher import ARC4
import os


def getpassandconfig(jfname):
    jar = zipfile.ZipFile(open(jfname, 'rb'))
    pw = StringIO(jar.read('a.txt')).read()
    config = StringIO(jar.read('b.txt')).read()
    ratdata = (pw, config)
    return ratdata


def decrypt_payload(ratdata):
    static_key = 'plowkmsssssPosq34r'
    rcobj = ARC4.new('{0}{1}{0}{1}{2}'.format(static_key, ratdata[0],'a'))
    data = rcobj.decrypt(ratdata[1])    
    return data


def extract_props(data):
    jtmp = StringIO()
    jtmp.write(data)
    jar = zipfile.ZipFile(jtmp)
    return StringIO(jar.read('org/jsocket/resources/config.json')).read()


def main():
    parser = argparse.ArgumentParser(description="Decrypt adwind jar.")
    parser.add_argument("jarfile", help="Adwind Jar file")
    parser.add_argument('-p', '--props', dest='props', action='store_true', help="Extract properties config.xml file.")
    parser.add_argument('-e', '--extract', dest='extract', action='store_true', help="Extract enctypted jar to out.jar.")

    args = parser.parse_args()
    rdata = getpassandconfig(args.jarfile)

    if not os.path.isfile(args.jarfile):
        raise Exception('File does not exist')

    if args.props:
        print 'Extracting Properties...'
        propdata = extract_props(decrypt_payload(rdata))
        out = open('config.json', 'wb')
        out.write(propdata)
        out.close()
        

    if args.extract:
        outfile = open('out.jar', 'wb')
        outfile.write(decrypt_payload(rdata))
        outfile.close()


if __name__ == '__main__':
    main()


