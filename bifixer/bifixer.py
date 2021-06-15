#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 21/06/2019 # Initial release # Marta Bañón"
__version__ = "Version 0.2 # 23/07/2019 # Non-Redis Bifixer # Marta Bañón"
__version__ = "Version 0.3 # 20/08/2019 # New feature: Segmentation # Marta Bañón"
__version__ = "Version 0.4 # 15/06/2021 # Easy install # Elsa Sarrías"


import os
import sys
import argparse
import time
import traceback
import logging
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
    import util
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
    # Input file
    parser.add_argument('input', type=argparse.FileType('rt'), default=None, help="Tab-separated files to be bifixed")
    # Output file (corpus)
    parser.add_argument('output', type=argparse.FileType('w'), default=sys.stdout, help="Fixed corpus")
    # Source language
    parser.add_argument("srclang", type=str, help="Source language (SL) of the input")
    # Target language
    parser.add_argument("trglang", type=str, help="Target language (TL) of the input")

    # Mandatory parameters
    groupM = parser.add_argument_group('Mandatory')

    # Options group
    groupO = parser.add_argument_group('Optional')
    # Format
    groupO.add_argument("--scol", default=3, type=util.check_positive, help="Source sentence column (starting in 1)")
    groupO.add_argument("--tcol", default=4, type=util.check_positive, help="Target sentence column (starting in 1)")
    groupO.add_argument("--sdeferredcol", type=util.check_positive, help="Source deferred standoff annotation column (starting in 1)")
    groupO.add_argument("--tdeferredcol", type=util.check_positive, help="Target deferred standoff annotation column (starting in 1)")
       

    # Character fixing
    groupO.add_argument('--ignore_characters', default=False, action='store_true', help="Doesn't fix mojibake, orthography, or other character issues")

    # Empty sides
    groupO.add_argument('--ignore_empty', default=False, action='store_true', help="Doesn't remove sentences with empty source or target")
    
    # Too long sides
    groupO.add_argument('--ignore_long', default=False, action='store_true', help="Doesn't ignore too long sentences")
    
    # Orthography
    groupO.add_argument('--ignore_orthography', default=False, action='store_true', help="Doesn't apply orthography fixing")

    # Deduplication
    groupO.add_argument('--ignore_duplicates', default=False, action='store_true', help="Doesn't obtain the hashes of parallel sentences")
    groupO.add_argument('--aggressive_dedup', default=False, action='store_true', help="Treats similar sentences as duplicates (marking them with the same hash)")

    # Segmentation
    groupO.add_argument('--ignore_segmentation', default=False, action='store_true', help="Doesn't change segmentation of long sentences")
    groupO.add_argument('--words_before_segmenting', default=15, type=util.check_positive, help="Max words allowed in one side of a parallel sentence before trying to segmentate it. Set to 0 to applicate segmentation on everything.")
    groupO.add_argument('--segmenter', default="nltk", type=str, choices=["nltk", "loomchild"], help="Segmenter module.")
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
    args.dedup = not args.ignore_duplicates  # more friendly usage of the ignore_duplicates flag

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
        chars_slang, charsRe_slang = restorative_cleaning.getCharsReplacements(args.srclang)
        chars_tlang, charsRe_tlang = restorative_cleaning.getCharsReplacements(args.trglang)

        punctChars_slang, punctRe_slang = restorative_cleaning.getNormalizedPunctReplacements(args.srclang)
        punctChars_tlang, punctRe_tlang = restorative_cleaning.getNormalizedPunctReplacements(args.trglang)

    if not args.ignore_orthography:
        replacements_slang = restorative_cleaning.getReplacements(args.srclang)
        replacements_tlang = restorative_cleaning.getReplacements(args.trglang)

    if not args.ignore_segmentation:
        source_segmenter = segmenter.NaiveSegmenter(args.srclang, args.segmenter)
        target_segmenter = segmenter.NaiveSegmenter(args.trglang, args.segmenter)

    for i in args.input:
        ilines += 1
        parts = i.split("\t")

        try:
            source_sentence = parts[args.scol - 1]
            target_sentence = parts[args.tcol - 1]
        except IndexError:
            logging.error(traceback.format_exc())
            logging.error("Wrong column index on line " + str(ilines))
            continue

        very_long = False

        # None of source or target sentences is empty:
        if args.ignore_empty or (source_sentence and target_sentence):
            if not args.ignore_long and (len(source_sentence) > 5000 or len(target_sentence) > 5000):
                very_long = True

            if not args.ignore_characters and not very_long:
                fixed_source = restorative_cleaning.fix(source_sentence, args.srclang, chars_slang, charsRe_slang, punctChars_slang, punctRe_slang)
                fixed_target = restorative_cleaning.fix(target_sentence, args.trglang, chars_tlang, charsRe_tlang, punctChars_tlang, punctRe_tlang)
            else:
                fixed_source = source_sentence.strip(" \n") 
                fixed_target = target_sentence.strip(" \n") 

            if not args.ignore_orthography and not very_long:
                corrected_source = restorative_cleaning.orthofix(fixed_source, replacements_slang)
                corrected_target = restorative_cleaning.orthofix(fixed_target, replacements_tlang)
            else:
                corrected_source = fixed_source
                corrected_target = fixed_target

            if not args.ignore_segmentation and (len(fixed_source.split()) > args.words_before_segmenting or len(fixed_target.split()) > args.words_before_segmenting) and not very_long:
                # The naive_segmenter must return an array of tuples (source sentence, target sentence)
                segments = segmenter.naive_segmenter(source_segmenter, target_segmenter, corrected_source, corrected_target)
            else:
                # keep original segmentation
                segments = [{"source_segment": corrected_source, "target_segment": corrected_target}]

            sent_num = 0
            for segment in segments:
                if not args.ignore_empty and (len(segment["source_segment"]) == 0 or len(segment["target_segment"]) == 0):
                    continue;
                if args.dedup:
                    if args.aggressive_dedup:
                        normalized_src = unidecode.unidecode(segment["source_segment"].lower().replace(" ", "").translate(str.maketrans('', '', string.punctuation + string.digits)))
                        normalized_trg = unidecode.unidecode(segment["target_segment"].lower().replace(" ", "").translate(str.maketrans('', '', string.punctuation + string.digits)))

                        segment_hash = xxh64(normalized_src + "\t" + normalized_trg).hexdigest()

                        charsum = sum(ord(ch) for ch in segment["source_segment"] + segment["target_segment"])

                        ranking = round(charsum / len(segment["source_segment"] + segment["target_segment"]), 2)

                    else:
                        segment_hash = xxh64(segment["source_segment"] + "\t" + segment["target_segment"]).hexdigest()
                        ranking = 1
                # if  dedupping: Add extra columnsn with hash and ranking in output file
                # Restored parts object, with the fixed segment, overwritten for each pair of extra segments,
                new_parts = parts

                new_parts[args.scol - 1] = segment["source_segment"]
                new_parts[args.tcol - 1] = segment["target_segment"]
                
                if len(segments) > 1:
                    sent_num += 1
                    if args.sdeferredcol and args.tdeferredcol:
                        if "#" in parts[args.sdeferredcol-1]:
                            if sent_num != int(parts[args.sdeferredcol-1].split('#')[1]):
                                continue
                        else:
                            new_parts[args.sdeferredcol-1] = parts[args.sdeferredcol-1].rstrip("\n")+"#"+str(sent_num)
                            new_parts[args.tdeferredcol-1] = parts[args.tdeferredcol-1].rstrip("\n")+"#"+str(sent_num)

                if args.ignore_empty or (new_parts[args.scol - 1] and new_parts[args.tcol - 1]):  # sentence sides may be empty now because it contained only spaces or similar weird thing
                    if (args.dedup):
                        # Remove the "/n" at the end of the last item
                        new_parts[-1] = str(new_parts[-1]).strip("\n")

                        new_parts.append(segment_hash)  # hash and ranking are added at the end
                        new_parts.append(ranking)
                        args.output.write("\t".join(str(v) for v in new_parts) + "\n")  # Convert to strings
                        # Remove hash and ranking for next iterations of loop
                        new_parts.pop()
                        new_parts.pop()
                    else:
                        # When no deduplicating:
                        new_parts[-1] = str(new_parts[-1]).strip("\n")
                        args.output.write("\t".join(str(v) for v in new_parts) + "\n")
                    olines += 1
                else:
                    # empty sides after processing
                    continue

        else:
            # source and/or target is empty
            continue


def perform_fixing(args):
    global ilines
    global olines

    time_start = default_timer()
    logging.info("Starting fixing text")
    fix_sentences(args)
    logging.info("Text fixing finished")

    # Stats
    logging.info("Finished")
    elapsed_time = default_timer() - time_start
    logging.info("Input lines: {0} rows".format(ilines))
    logging.info("Output lines: {0} rows".format(olines))
    logging.info("Elapsed time {0:.2f} s".format(elapsed_time))
    logging.info("Troughput: {0} rows/s".format(int((ilines * 1.0) / elapsed_time)))

    logging.info("Output file: {0}".format(os.path.abspath(args.output.name)))


def main(args):
    logging.info("Executing main program...")
    perform_fixing(args)
    logging.info("Program finished")


if __name__ == '__main__':
    try:
        util.logging_setup()
        args = initialization()  # Parsing parameters
        main(args)  # Running main program
    except Exception as ex:
        tb = traceback.format_exc()
        logging.error(tb)
        sys.exit(1)
