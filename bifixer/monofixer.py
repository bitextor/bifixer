#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 21/06/2019 # Initial release # Marta Bañón"
__version__ = "Version 0.2 # 23/07/2019 # Non-Redis Bifixer # Marta Bañón"
__version__ = "Version 0.3 # 20/08/2019 # New feature: Segmentation # Marta Bañón"
__version__ = "Version 0.4 # 03/02/2020 # Monofixer # Marta Bañón"


import os
import sys
import argparse
import copy
import traceback
import logging 

from unicodedata import category as cat
from unidecode import unidecode
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

# Translate table to remove non alphabetic characters
tbl = [chr(i) for i in range(sys.maxunicode) if not cat(chr(i)).startswith('L')]
remove_non_alpha = str.maketrans('', '', ''.join(tbl))


def initialization():
    global ilines
    global olines

    
    ilines = 0    
    olines = 0
    header = "--header" in sys.argv
    
    logging.info("Processing arguments...")
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.ArgumentDefaultsHelpFormatter, description=__doc__)
    
    # Mandatory parameters
    #Input file
    parser.add_argument('input', type=argparse.FileType('rt'), default=None, help="Tab-separated file to be fixed")
    #Output file (corpus)
    parser.add_argument('output', type=argparse.FileType('w'), default=sys.stdout, help="Fixed corpus")
    #Language
    parser.add_argument("lang", type=str, help="Language of the input")

    # Options group
    groupO = parser.add_argument_group('Optional')
    #Format
    groupO.add_argument("--header", action='store_true', help="Input file will have header")
    groupO.add_argument("--scol", type=util.check_positive if not header else str, default=2 if not header else "src_text", help ="Sentence column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--sdeferredcol", type=util.check_positive if not header else str, help="Source deferred standoff annotation column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--sparagraphid", type=util.check_positive if not header else str, help="Source paragraph identification column (starting in 1). The name of the field is expected instead of the position if --header is set")

    #Character fixing
    groupO.add_argument('--ignore_characters', default=False, action='store_true', help="Doesn't fix mojibake, orthography, or other character issues")
    groupO.add_argument('--ignore_normalization', default=False, action='store_true', help="Doesn't normalize punctuation and spaces.")

    # HTML tags
    groupO.add_argument('--ignore_html', default=False, action='store_true', help="Doesn't remove HTML tags")
  
    #Empty sides
    groupO.add_argument('--ignore_empty', default=False, action='store_true', help="Doesn't remove empty sentences")

    # Too long sentences
    groupO.add_argument('--ignore_long', default=False, action='store_true', help="Doesn't ignore too long sentences")

    #Orthography
    groupO.add_argument('--ignore_orthography', default=False, action='store_true', help="Doesn't apply orthography fixing")

    # Common detokenization issues
    groupO.add_argument('--ignore_detokenization', default=False, action='store_true', help="Doesn't fix common tokenization issues")

    
    #Deduplication
    groupO.add_argument('--ignore_duplicates', default=False, action='store_true', help="Doesn't obtain the hashes of sentences")    

    groupO.add_argument('--aggressive_dedup', default=False, action='store_true', help="Treats similar sentences as duplicates (marking them with the same hash)")

    #Segmentation
    groupO.add_argument('--ignore_segmentation' , default=False, action='store_true', help="Doesn't change segmentation of long sentences")
    groupO.add_argument('--words_before_segmenting', default=15, type=util.check_positive, help="Max words allowed in a parallel sentence before trying to segmentate it. Set to 0 to applicate segmentation on everyt33hing.")
    groupO.add_argument('--segmenter', default="nltk", type=str, choices=["nltk", "loomchild"], help="Segmenter module.")    
    groupO.add_argument('--tmp_dir', default=gettempdir(), help="Temporary directory where creating the temporary files of this program")


    # Annotation
    groupO.add_argument('--annotated_output', default=False, action='store_true', help="Adds an extra column indicating if the sentence was modified ('Yes' if it was modified, otherwise 'No')")
    
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


    logging.debug("Arguments processed: {}".format(str(args)))
 
    logging.info("Arguments processed.")
     

    return args


def fix_sentences(args):
    if ('ilines' in globals() and 'olines' in globals()):
        global ilines
        global olines        
    else:
        ilines = 0
        olines = 0    

    if not args.ignore_characters:
        chars_lang, charsRe_lang = restorative_cleaning.getCharsReplacements(args.lang)

    if not args.ignore_normalization:
        punctChars_lang, punctRe_lang = restorative_cleaning.getNormalizedPunctReplacements(args.lang)

    if not args.ignore_orthography:    
        replacements_lang = restorative_cleaning.getReplacements(args.lang)
      
    if not args.ignore_detokenization:
        detoks_lang = restorative_cleaning.getDetokenizations(args.lang)
        
    if not args.ignore_segmentation:
        lang_segmenter = segmenter.NaiveSegmenter(args.lang, args.segmenter)

    if args.header:
        header = next(args.input).strip().split("\t")

        # Transform fields to idxs
        if args.scol not in header:
            raise Exception(f"The provided --scol '{args.scol}' is not in the input header")

        args.scol = int(header.index(args.scol)) + 1

        if args.sdeferredcol:
            if args.sdeferredcol not in header:
                raise Exception(f"The provided --sdeferredcol '{args.sdeferredcol}' is not in the input header")

            args.sdeferredcol = int(header.index(args.sdeferredcol)) + 1
        if args.sparagraphid:
            if args.sparagraphid not in header:
                raise Exception(f"The provided --sparagraphid '{args.sparagraphid}' is not in the input header")

            args.sparagraphid = int(header.index(args.sparagraphid)) + 1

        # Write the output header once
        args.output.write("\t".join(header))

        if args.dedup:
            args.output.write("\tbifixer_hash\tbifixer_score")

        if args.annotated_output:
            args.output.write("\tbifixed")

        args.output.write("\n")

    for i in args.input:
        ilines += 1
        parts = i.split("\t")

        try:
            sentence = parts[args.scol-1]

            # Check optional indexes
            if args.sdeferredcol:
                parts[args.sdeferredcol-1]
            if args.sparagraphid:
                parts[args.sparagraphid-1]

        except IndexError:
            logging.error(traceback.format_exc())
            logging.error("Wrong column index on line " + str(ilines))
            continue
            
        very_long = False

        if not args.ignore_long and (len(sentence) > 5000):
                very_long = True

        if not args.ignore_characters and not very_long:        
           fixed_sentence = restorative_cleaning.fix(sentence, args.lang, chars_lang, charsRe_lang)
        else:
            fixed_sentence = sentence

        if not args.ignore_html and not very_long:
                fixed_sentence = restorative_cleaning.remove_html_tags(fixed_sentence)
                
        if not args.ignore_normalization:
            fixed_sentence = restorative_cleaning.normalize(fixed_sentence, args.lang, punctChars_lang, punctRe_lang)
                
        if not args.ignore_orthography and not very_long:    
            corrected_sentence = restorative_cleaning.ortho_detok_fix(fixed_sentence, replacements_lang, detoks_lang)
        else:
            corrected_sentence = fixed_sentence
                
        if not args.ignore_segmentation and (len(fixed_sentence.split()) > args.words_before_segmenting) and not very_long:
            segments = segmenter.naive_segmenter_mono(lang_segmenter, corrected_sentence) 

        else:
            #keep original segmentation    
            segments = [corrected_sentence]

        sent_num = 0        

        for segment in segments:
            if not args.ignore_empty and len(segment) == 0:
                continue
            if args.dedup:
                if args.aggressive_dedup:
                    #normalized_sentence = unidecode.unidecode(segment.lower().replace(" ", "").translate(str.maketrans('', '', string.punctuation+string.digits)))
                    normalized_sentence = unidecode(segment.lower().translate(remove_non_alpha))
                    hash = xxh64(normalized_sentence).hexdigest()
                        
                    charsum = sum(ord(ch) for ch in segment)
                    if len(segment) == 0:
                        ranking = 0.0
                    else:
                        ranking = round(charsum/len(segment),2)

                else:
                    hash = xxh64(segment).hexdigest()
                    ranking = 1
            #if  dedupping: Add extra columnsn with hash and ranking in output file
            #Restored parts object, with the fixed segment, overwritten for each extra segment
            new_parts = copy.deepcopy(parts)
            new_parts[args.scol-1] = segment
            
            if len(segments) > 1:
                sent_num += 1
                if args.sdeferredcol:
                    if "#" in parts[args.sdeferredcol-1]:
                        # Reconstruction
                        if sent_num != int(parts[args.sdeferredcol-1].split('#')[1]):
                            continue
                    else:
                        new_parts[args.sdeferredcol-1] = parts[args.sdeferredcol-1].rstrip("\n")+"#"+str(sent_num)

                if args.sparagraphid:
                    new_parts[args.sparagraphid-1] = parts[args.sparagraphid-1].rstrip("\n")+"#"+str(sent_num)

            #Remove the "/n" at the end of the last item
            new_parts[-1]= str(new_parts[-1]).strip("\n")

            # sentence may be empty now because it contained only spaces or similar weird thing
            # for a sentence containing only spaces but not normalized, strip it
            if args.ignore_empty or (new_parts[args.scol-1].strip()):
                if (args.dedup):
                    new_parts.append(hash) #hash and ranking are added at the end           
                    new_parts.append(ranking)
                    
                    if args.annotated_output:
                        if (new_parts[args.scol -1].strip("\n") != sentence.strip("\n")):
                            new_parts.append("Yes")
                        else:
                            new_parts.append("No")
                                
                    
                    args.output.write("\t".join(str(v) for v in new_parts)+"\n")  #Convert to strings
                    #Remove hash and ranking for next iterations of loop
                    new_parts.pop()
                    new_parts.pop()
                    if args.annotated_output:
                        new_parts.pop()
                else:                   
                    #When no deduplicating:
                    if args.annotated_output:
                        if (new_parts[args.scol -1].strip("\n") != sentence.strip("\n")):
                            new_parts.append("Yes")
                        else:
                            new_parts.append("No")
                    args.output.write("\t".join(str(v) for v in new_parts)+"\n")
                    if args.annotated_output:
                        new_parts.pop()
                olines += 1
            else:
                #empty sentence after processing
                continue    
                    
          
            
def perform_fixing(args):
    global ilines
    global olines
    
    
    time_start=default_timer()
    logging.info("Starting fixing text")    
    fix_sentences(args)
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
        
