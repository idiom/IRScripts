import hashlib
from StringIO import StringIO
import zipfile
import argparse
from Crypto.Cipher import ARC4
import os

'''
    Script to extract encrypted Adwind/AlienSpy Rat

    Payload is RC4 encrypted within the config.ini file.

    Key is composed of the SHA256 value of password.ini string + ALSKEOPQLFKJDUSIKSJAUIE
    The static string is set in the LoadPassword class.

'''


def getpassandconfig(jfname):
    jar = zipfile.ZipFile(open(jfname, 'rb'))
    pw = StringIO(jar.read('password.ini')).read()
    config = StringIO(jar.read('config.ini')).read()
    ratdata = (pw, config)
    return ratdata

def decryptpayload(ratdata):
    static_key = 'ALSKEOPQLFKJDUSIKSJAUIE'
    rcobj = ARC4.new(hashlib.sha256(ratdata[0]+static_key).hexdigest())
    data = rcobj.decrypt(ratdata[1])
    return data

def extractprops(data):
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
        propdata = extractprops(decryptpayload(rdata))
        out = open('config.xml', 'wb')
        out.write(propdata)
        out.close()

    if args.extract:
        outfile = open('out.jar', 'wb')
        outfile.write(decryptpayload(rdata))
        outfile.close()


if __name__ == '__main__':
    main()


