__description__ = 'AlienSpy Decoder'
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
    pw = StringIO(jar.read('password.ini')).read()
    config = StringIO(jar.read('config.ini')).read()
    ratdata = (pw, config)
    return ratdata


def decrypt_payload(ratdata):
    static_key = 'ALSKEOPQLFKJDUSIKSJAUIE'
    rcobj = ARC4.new(hashlib.sha256(ratdata[0]+static_key).hexdigest())
    data = rcobj.decrypt(ratdata[1])
    return data


def extract_props(data):
    jtmp = StringIO()
    jtmp.write(data)
    jar = zipfile.ZipFile(jtmp)
    return StringIO(jar.read('config.xml')).read()


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
        out = open('config.xml', 'wb')
        out.write(propdata)
        out.close()

    if args.extract:
        outfile = open('out.jar', 'wb')
        outfile.write(decrypt_payload(rdata))
        outfile.close()


if __name__ == '__main__':
    main()


