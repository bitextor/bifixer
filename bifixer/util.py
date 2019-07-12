#!/usr/bin/env python

import os 
import sys
import argparse
import subprocess
import time
import logging
import redis
import traceback

from itertools import zip_longest

# Logging config
def logging_setup(args = None):
    logger = logging.getLogger()
    logger.handlers = [] # Removing default handler to avoid duplication of log messages
    logger.setLevel(logging.ERROR)
    
    h = logging.StreamHandler(sys.stderr)
    if args != None:
       h = logging.StreamHandler(args.logfile)
      
    h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    #logger.setLevel(logging.INFO)
    
    if args != None:
        if not args.quiet:
            logger.setLevel(logging.INFO)
        if args.debug:
            logger.setLevel(logging.DEBUG)
            

# Check if the argument of a program (argparse) is strictly positive
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def purge_redis(r):
     r.flushdb()
     

def start_redis(args):
     r = redis.StrictRedis(host=args.redis_host, port=args.redis_port, password=args.redis_password, db=args.redis_db, decode_responses=True)
     try:
        r.ping()
     except redis.exceptions.ConnectionError as ce:
        logging.warning("Redis offline, starting it.")
        subprocess.Popen(["redis-server"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        time.sleep(1)        
     try:   
        purge_redis(r)
     except Exception as e:
         logging.error(traceback.format_exc())
         logging.error("Failed to connect with Redis in {0}:{1}".format(args.redis_host, args.redis_port))
         sys.exit(1)



def connect_redis(args):
     redis_dict = redis.StrictRedis(host=args.redis_host, port=args.redis_port, password=args.redis_password,db=args.redis_db, decode_responses=True)
     try:
         redis_dict.ping()
     except redis.exceptions.ConnectionError as ce:
         logging.warning("Redis offline, starting it.")
         subprocess.Popen(["redis-server"], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
         time.sleep(1)
     
     try:
         #At this point if Redis isn't up it won't be D:
         #redis_dict.flushall()
         redis_dict.config_set("dir", args.tmp_dir)
     except Exception as e:
         logging.error(traceback.format_exc())
         logging.error("Failed to connect with Redis in {0}:{1}".format(args.redis_host, args.redis_port))
         sys.exit(1)
     return redis_dict    

