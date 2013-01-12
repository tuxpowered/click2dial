#!/usr/bin/env python
"""
SYNOPSIS

    TODO click2dial.py [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    Proivde a URL to iniate calls to a desired number, and internal extension.
    Usage: http://asterisk-pbx:port?did=number2dial&i_exten=1234&key=licensekey&m=json&crm=ns

    Only the did and i_exten are required at this point.
    This version will based on the usage of asterisk .call files, to start the process. I hope
    to possibly migrate to using AMI options with asterisks built in http support, but maybe
    that is not what is best. For now this is dirty quick and should be effective.

EXAMPLES

    click2dial.py --destination=5555551212 --internal=1000

EXIT STATUS

    TODO: List exit codes

AUTHOR

    Ben DAVIS <ben@sjobeck.com>

LICENSE

    This script is for internal usage only.

VERSION

    $Id$
"""

import sys
import os
import traceback
import optparse
import time
import re
#from pexpect import run, spawn

import logging
logname = 'click2dial'
logger = logging.getLogger(logname)
hdlr = logging.FileHandler('/var/log/%s.log' % (logname) )
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
logger.info('Starting logger')

# We need our magical pycall library to create our call files all nice
# and python like. :)

try:
    logger.info('Attempting to load pycall library.')
    import pycall
except Exception, e:
    logger.warn('Unable to load pycall library. Please visit http://pycall.org/.')
    logger.warn('System unable to proceed.')
    sys.exit(1)


def mkCall():
    """Wrapper around mkCallFile, and mkCallAMI functions to use what ever is best"""
    mkCallFile()

def mkCallFile(number2dial=None, extension=None, **kwargs):
    """Creates call file for us"""

    # Removes all non alpha chars from the number2dial

    vars = {'num2dial':number2dial,'accountcode':'TESTING'}
    call = pycall.Call('IAX2/osdorp/%s' %(extension.strip()),
                       variables=vars,
                       account='TESTING',
                       callerid='Testing <%s000000>' %(extension))
    # We want to send this call to an existing context in asterisk
    context = pycall.Context('click2dial', 's', '1')

    # Build the call file in memory
    cfile = pycall.CallFile(call, context, user='asterisk')

    # Send the call file to the spool
    cfile.spool()
    return cfile.contents

def main ():

    global options, args
    # TODO: Do something more interesting here...
    print options
    print args

if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                       usage=globals()['__doc__'],
                                       version='0.1')
        parser.add_option ('-v',
                           '--verbose',
                           action='store_true',
                           default=False,
                           help='verbose output')

        parser.add_option ('-d',
                           '--destination',
                           action='store_true',
                           default=False,
                           help='Called party telephone number.')

        parser.add_option ('-e',
                           '--exten',
                           action='store_true',
                           default=False,
                           help='Internal extension.')

        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
        if options.verbose: print time.asctime()
        main()
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(0)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        traceback.print_exc()
        os._exit(1)
