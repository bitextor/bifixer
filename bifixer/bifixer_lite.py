#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 21/06/2019 # Initial release # Marta Bañón"

import os
import sys
import argparse
import subprocess
import shutil
import time
import traceback
import logging 
import hashlib
import redis    
import unidecode
import string

from tempfile import gettempdir
from timeit import default_timer
from xxhash import xxh64

try:
    from . import util
    from . import restorative_cleaning
    from . import segmenter
except (ImportError, SystemError):
    import  util    
    import restorative_cleaning
    import segmenter

def initialization():
    global ilines
    global olines

    
    ilines = 0    
    olines = 0
    
    logging.info("Processing arguments...")
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)
    
    # Mandatory parameters
    #Input file
    parser.add_argument('input', type=argparse.FileType('rt'), default=None, help="Tab-separated files to be bifixed")  
    #Output file (corpus)
    parser.add_argument('output', type=argparse.FileType('w'), default=sys.stdout, help="Fixed corpus")        
    #Source language
    parser.add_argument("srclang", type=str, help="Source language (SL) of the input")
    #Target language
    parser.add_argument("trglang", type=str, help="Target language (TL) of the input")

    #Mandatory parameters
    groupM = parser.add_argument_group('Mandatory')
    #Redis DB index
    groupM.add_argument('--redis_db',required=True, help="Redis database index")

    # Options group
    groupO = parser.add_argument_group('Optional')
    #Format
    groupO.add_argument("--scol", default=3, type=util.check_positive, help ="Source sentence column (starting in 1)")
    groupO.add_argument("--tcol", default=4, type=util.check_positive, help ="Target sentence column (starting in 1)")    
    groupO.add_argument("--sucol", default=1, type=util.check_positive, help ="Source URL column (starting in 1)")    
    groupO.add_argument("--tucol", default=2, type=util.check_positive, help ="Target URL column (starting in 1)")    
    #Character fixing
    groupO.add_argument('--ignore_characters', default=False, action='store_true', help="Doesn't fix mojibake, orthography, or other character issues")
    #Deduplication
    groupO.add_argument('--ignore_duplicates', default=False, action='store_true', help="Doesn't remove duplicated parallel sentences")    
    groupO.add_argument('--ignore_empty', default=False, action='store_true', help="Doesn't remove sentences with empty source or target")    
    groupO.add_argument('--ignore_urls' , default=False, action='store_true', help="Doesn't save an URLs file when deduplicating")
    groupO.add_argument('--aggressive_dedup', default=False, action='store_true', help="Treats similar sentences as duplicates (removing them)")
    #Redis
    groupO.add_argument('--redis_host', default="localhost", help="Redis host")
    groupO.add_argument('--redis_port', default="6379", help="Redis port")
    groupO.add_argument('--redis_password', default="", help="Redis password")
    #Segmentation
    groupO.add_argument('--ignore_segmentation' , default=False, action='store_true', help="Doesn't change segmentation of long sentences")
    groupO.add_argument('--words_before_segmenting', default=40, type=util.check_positive, help="Max words allowed in one side of a parallel sentence before trying to segmentate it. Set to 0 to applicate segmentation on everything.")
    
    groupO.add_argument('--tmp_dir', default=gettempdir(), help="Temporary directory where creating the temporary files of this program")
    
    # Logging group
    groupL = parser.add_argument_group('Logging')
    groupL.add_argument('-q', '--quiet', action='store_true', help='Silent logging mode')
    groupL.add_argument('--debug', action='store_true', help='Debug logging mode')
    groupL.add_argument('--logfile', type=argparse.FileType('a'), default=sys.stderr, help="Store log to a file")
    groupL.add_argument('-v', '--version', action='version', version="%(prog)s " + __version__, help="show version of this script and exit")
 
    # Validating & parsing
    args = parser.parse_args()
    util.logging_setup(args)
    args.dedup = not args.ignore_duplicates  #more friendly usage of the ignore_duplicates flag
    args.save_urls = not args.ignore_urls #more friendly usage of the ignore_urls flag
        
    
    logging.debug("Arguments processed: {}".format(str(args)))
 
    logging.info("Arguments processed.")
     

    return args


def fix_sentences(args, hashes):
    global ilines
    global olines

    if not args.ignore_characters:
        chars_replacements_slang, charsRe_slang = restorative_cleaning.getCharsReplacements(args.srclang)
        chars_replacements_tlang, charsRe_tlang = restorative_cleaning.getCharsReplacements(args.trglang)

        commonRegexs = restorative_cleaning.getCommonRegexs()

        replacements_slang = restorative_cleaning.getReplacements(args.srclang)
        replacements_tlang = restorative_cleaning.getReplacements(args.trglang)
    if args.dedup:
        batch = []
        pipeline = hashes.pipeline(transaction=False)
            
    for i in args.input:
        ilines += 1
        parts = i.split("\t")

        try:
            source_sentence = parts[args.scol-1]
            target_sentence = parts[args.tcol-1]
            if args.dedup and args.save_urls:            
                source_url = parts[args.sucol-1]
                target_url = parts[args.tucol-1]
        except IndexError:
            logging.error(traceback.format_exc())
            logging.error("Wrong column index")
            sys.exit(1)
        
        #None of source or target sentences is empty:
        if args.ignore_empty or (source_sentence and target_sentence):
            if not args.ignore_characters:        
                fixed_source = restorative_cleaning.fix(source_sentence, args.srclang, chars_replacements_slang, charsRe_slang, commonRegexs, replacements_slang)
                fixed_target = restorative_cleaning.fix(target_sentence, args.trglang, chars_replacements_tlang, charsRe_tlang, commonRegexs, replacements_tlang)
            else:
                fixed_source = source_sentence
                fixed_target = target_sentence    


            if not args.ignore_segmentation and (len(fixed_source.split()) > args.words_before_segmenting or len(fixed_target.split()) > args.words_before_segmenting):
                #The naive_segmenter must return an array of tuples (source sentence, target sentence)             
                segments = segmenter.naive_segmenter(fixed_source, fixed_target)                
            else:
                #keep original segmentation    
                segments = [{"source_segment": fixed_source, "target_segment": fixed_target}]
                
            for segment in segments:
                if args.dedup:
                    if args.aggressive_dedup:
                        normalized_src = unidecode.unidecode(segment["source_segment"].lower().replace(" ", "").translate(str.maketrans('', '', string.punctuation)))
                        normalized_trg = unidecode.unidecode(segment["target_segment"].lower().replace(" ", "").translate(str.maketrans('', '', string.punctuation)))   
                        #hash = hashlib.md5((normalized_src+"\t"+normalized_trg).encode()).hexdigest()
                        hash = xxh64(normalized_src+"\t"+normalized_trg).hexdigest()
                    else:
                        #hash = hashlib.md5((segment["source_segment"]+"\t"+segment["target_segment"]).encode()).hexdigest()
                        hash = xxh64(segment["source_segment"]+"\t"+segment["target_segment"]).hexdigest()
                #if  dedupping: put source, target, hash, extra in output file, and store hashes and urls in the urls object
                #Restored parts object, with the fixed segment, overwritten for each pair of extra segments,
                #the idea is to keep the order the columns came in
                new_parts = parts
                
                new_parts[args.scol-1] = segment["source_segment"]
                new_parts[args.tcol-1] = segment["target_segment"]
                
                if (args.dedup):
                    #Remove the "/n" at the end of the last item
                    new_parts[-1]= new_parts[-1].strip("\n")
                
                    new_parts.append(hash) #hash is added at the end           


                    new_parts.pop(max(args.sucol-1, args.tucol-1)) #remove first the one with the greater index, so it doesn't affect to the other index
                    new_parts.pop(min(args.sucol-1, args.tucol-1)) #and then remove the other

                    if args.save_urls:
                        url_pair=[source_url,target_url]
                    else:
                        url_pair = ["SRC URL", "TRG URL"]  #Even when not saving urls, Redis must contain something associated for the hash.
                    
                        
                    #rpush: Returns the length of the list after the push
                    #operation.  
                    batch.append(new_parts)
                    pipeline.rpush(hash, *url_pair)

                else:                   
                    #When no deduplicating:
                    args.output.write("\t".join(new_parts))
                    olines += 1
                    
        else:
        #source and/or target is empty
            continue
        if args.dedup and olines >= 3500:  #ilines % 1000 == 0:
            responses = pipeline.execute()
            for sentence, urls_size in zip(batch,responses):
                if urls_size <= 2 :  #source+target: only one parallel sentence
                #It's not a duplicate: put it in the output
                    args.output.write("\t".join(sentence))
                    args.output.write("\n")
                    olines += 1

            batch.clear()
            pipeline.reset()
    else:
    #End of the for loop
        if args.dedup and len(batch) > 0:
            responses = pipeline.execute()
            for sentence, urls_size in zip(batch, responses):
                if urls_size <= 2 : 
                    args.output.write("\t".join(sentence))
                    args.output.write("\n")
                    olines += 1
            batch.clear()
            pipeline.reset()        
            
def perform_fixing(args):
    global ilines
    global olines
    hashes = None
    
    if args.dedup:
        hashes = util.connect_redis(args)
    
    time_start=default_timer()
    logging.info("Starting fixing text")    
    fix_sentences(args, hashes)
    logging.info("Text fixing finished")

    # Stats
    logging.info("Finished")
    elapsed_time = default_timer() - time_start
    logging.info("Input lines: {0} rows".format(ilines))
    logging.info("Output lines: {0} rows".format(olines))
    logging.info("Elapsed time {0:.2f} s".format(elapsed_time))
    logging.info("Troughput: {0} rows/s".format(int((ilines*1.0)/elapsed_time)))

    logging.info("Output file: {0}".format(os.path.abspath(args.output.name)))

    
def main(args):
    logging.info("Executing main program...")
    perform_fixing(args)
    logging.info("Program finished")    


if __name__ == '__main__':
    try:
        util.logging_setup()
        args = initialization() # Parsing parameters
        main(args)  # Running main program
    except Exception as ex:
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(1)