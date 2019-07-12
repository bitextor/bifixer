#!/usr/bin/env python

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 04/07/2019 # Initial release # Marta Bañón"

import traceback
import logging
import sys
import argparse
import os

try:
    from . import util
except (ImportError, SystemError):
    import  util

def initialization():
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)
    
    groupM = parser.add_argument_group('Mandatory')
    groupM.add_argument('--redis_db',required=True, help="Redis database index")    
    
    groupO = parser.add_argument_group('Optional')
    groupO.add_argument('--redis_host', default="localhost", help="Redis host")
    groupO.add_argument('--redis_port', default="6379", help="Redis port")
    groupO.add_argument('--redis_password', default="", help="Redis password")
    

    # Logging group
    groupL = parser.add_argument_group('Logging')
    groupL.add_argument('-q', '--quiet', action='store_true', help='Silent logging mode')
    groupL.add_argument('--debug', action='store_true', help='Debug logging mode')
    groupL.add_argument('--logfile', type=argparse.FileType('a'), default=sys.stderr, help="Store log to a file")
    groupL.add_argument('-v', '--version', action='version', version="%(prog)s " + __version__, help="show version of this script and exit")

    # Validating & parsing
    args = parser.parse_args()
    util.logging_setup(args)

    logging.debug("Arguments processed: {}".format(str(args)))

    return args

def setup_bifixer(args):
    util.start_redis(args)    

def main(args):
    logging.info("Executing setup for bifixer...")
    setup_bifixer(args)
    logging.info("Setup finished")


if __name__ == '__main__':
    try:
        util.logging_setup()
        args = initialization() # Parsing parameters
        main(args)  # Running main program
    except Exception as ex:
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(1)
