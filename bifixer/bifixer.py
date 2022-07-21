#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 21/06/2019 # Initial release # Marta Bañón"
__version__ = "Version 0.2 # 23/07/2019 # Non-Redis Bifixer # Marta Bañón"
__version__ = "Version 0.3 # 20/08/2019 # New feature: Segmentation # Marta Bañón"
__version__ = "Version 0.4 # 15/06/2021 # Easy install # Elsa Sarrías"
__version__ = "Version 0.5 # 22/06/2021 # Replacements improvements and fix tokenization for Maltese # Jaume Zaragoza"
__version__ = "Version 0.7 # 15/02/2022 # Disable punctuation normalization # Jaume Zaragoza"
__version__ = "Version 0.8 # 15/06/2022 # Remove HTML tags # Marta Bañón"

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
    import util
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
    # Input file
    parser.add_argument('input', type=argparse.FileType('rt', encoding='UTF-8'), default=None, help="Tab-separated files to be bifixed")
    # Output file (corpus)
    parser.add_argument('output', type=argparse.FileType('w'), default=sys.stdout, help="Fixed corpus")
    # Source language
    parser.add_argument("srclang", type=str, help="Source language (SL) of the input")
    # Target language
    parser.add_argument("trglang", type=str, help="Target language (TL) of the input")

    # Options group
    groupO = parser.add_argument_group('Optional')
    # Format
    groupO.add_argument("--header", action='store_true', help="Input file will have header")
    groupO.add_argument("--scol", type=util.check_positive if not header else str, default=3 if not header else "src_text", help="Source sentence column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--tcol", type=util.check_positive if not header else str, default=4 if not header else "trg_text", help="Target sentence column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--sdeferredcol", type=util.check_positive if not header else str, help="Source deferred standoff annotation column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--tdeferredcol", type=util.check_positive if not header else str, help="Target deferred standoff annotation column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--sparagraphid", type=util.check_positive if not header else str, help="Source paragraph identification column (starting in 1). The name of the field is expected instead of the position if --header is set")
    groupO.add_argument("--tparagraphid", type=util.check_positive if not header else str, help="Target paragraph identification column (starting in 1). The name of the field is expected instead of the position if --header is set")

    # Character fixing
    groupO.add_argument('--ignore_characters', default=False, action='store_true', help="Doesn't fix mojibake or other character issues")
    groupO.add_argument('--ignore_normalization', default=False, action='store_true', help="Doesn't normalize punctuation and spaces.")

    # HTML tags
    groupO.add_argument('--ignore_html', default=False, action='store_true', help="Doesn't remove HTML tags")

    # Empty sides
    groupO.add_argument('--ignore_empty', default=False, action='store_true', help="Doesn't remove sentences with empty source or target")
    
    # Too long sides
    groupO.add_argument('--ignore_long', default=False, action='store_true', help="Doesn't ignore too long sentences")
    
    # Orthography
    groupO.add_argument('--ignore_orthography', default=False, action='store_true', help="Doesn't apply orthography fixing")

    # Common detokenization issues
    groupO.add_argument('--ignore_detokenization', default=False, action='store_true', help="Doesn't fix common tokenization issues")

    # Deduplication
    groupO.add_argument('--ignore_duplicates', default=False, action='store_true', help="Doesn't obtain the hashes of parallel sentences")
    groupO.add_argument('--aggressive_dedup', default=False, action='store_true', help="Treats similar sentences as duplicates (marking them with the same hash)")

    # Segmentation
    groupO.add_argument('--ignore_segmentation', default=False, action='store_true', help="Doesn't change segmentation of long sentences")
    groupO.add_argument('--words_before_segmenting', default=15, type=util.check_positive, help="Max words allowed in one side of a parallel sentence before trying to segmentate it. Set to 0 to applicate segmentation on everything.")
    groupO.add_argument('--segmenter', default="nltk", type=str, choices=["nltk", "loomchild"], help="Segmenter module.")
    groupO.add_argument('--tmp_dir', default=gettempdir(), help="Temporary directory where creating the temporary files of this program")
    
    # Annotation
    groupO.add_argument('--annotated_output', default=False, action='store_true', help="Adds an extra column indicating if the sentence pair was modified ('Yes' if it was modified, otherwise 'No')")

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

    if not args.ignore_normalization:
        punctChars_slang, punctRe_slang = restorative_cleaning.getNormalizedPunctReplacements(args.srclang)
        punctChars_tlang, punctRe_tlang = restorative_cleaning.getNormalizedPunctReplacements(args.trglang)
        
    if not args.ignore_orthography:
        replacements_slang = restorative_cleaning.getReplacements(args.srclang)
        replacements_tlang = restorative_cleaning.getReplacements(args.trglang)

    if not args.ignore_detokenization:
        detoks_slang = restorative_cleaning.getDetokenizations(args.srclang)
        detoks_tlang = restorative_cleaning.getDetokenizations(args.trglang)

    if not args.ignore_segmentation:
        source_segmenter = segmenter.NaiveSegmenter(args.srclang, args.segmenter)
        target_segmenter = segmenter.NaiveSegmenter(args.trglang, args.segmenter)

    if args.header:
        header = next(args.input).strip().split("\t")

        # Transform fields to idxs
        if args.scol not in header:
            raise Exception(f"The provided --scol '{args.scol}' is not in the input header")
        if args.tcol not in header:
            raise Exception(f"The provided --tcol '{args.tcol}' is not in the input header")

        args.scol = int(header.index(args.scol)) + 1
        args.tcol = int(header.index(args.tcol)) + 1

        if args.sdeferredcol:
            if args.sdeferredcol not in header:
                raise Exception(f"The provided --sdeferredcol '{args.sdeferredcol}' is not in the input header")

            args.sdeferredcol = int(header.index(args.sdeferredcol)) + 1
        if args.tdeferredcol:
            if args.tdeferredcol not in header:
                raise Exception(f"The provided --tdeferredcol '{args.tdeferredcol}' is not in the input header")

            args.tdeferredcol = int(header.index(args.tdeferredcol)) + 1
        if args.sparagraphid:
            if args.sparagraphid not in header:
                raise Exception(f"The provided --sparagraphid '{args.sparagraphid}' is not in the input header")

            args.sparagraphid = int(header.index(args.sparagraphid)) + 1
        if args.tparagraphid:
            if args.tparagraphid not in header:
                raise Exception(f"The provided --tparagraphid '{args.tparagraphid}' is not in the input header")

            args.tparagraphid = int(header.index(args.tparagraphid)) + 1

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
            source_sentence = parts[args.scol - 1]
            target_sentence = parts[args.tcol - 1]

            # Check optional indexes
            if args.sdeferredcol and args.tdeferredcol:
                parts[args.sdeferredcol - 1]
                parts[args.tdeferredcol - 1]
            if args.sparagraphid and args.tparagraphid:
                parts[args.sparagraphid - 1]
                parts[args.tparagraphid - 1]
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
                fixed_source = restorative_cleaning.fix(source_sentence, args.srclang, chars_slang, charsRe_slang)
                fixed_target = restorative_cleaning.fix(target_sentence, args.trglang, chars_tlang, charsRe_tlang)
            else:
                fixed_source = source_sentence.strip(" \n") 
                fixed_target = target_sentence.strip(" \n") 

            if not args.ignore_html and not very_long:
                fixed_source = restorative_cleaning.remove_html_tags(fixed_source)
                fixed_target = restorative_cleaning.remove_html_tags(fixed_target)            
                
            if not args.ignore_normalization and not very_long:
                fixed_source = restorative_cleaning.normalize(fixed_source, args.srclang, punctChars_slang, punctRe_slang)
                fixed_target = restorative_cleaning.normalize(fixed_target, args.trglang, punctChars_tlang, punctRe_tlang)

            if not args.ignore_orthography and not very_long:
                corrected_source = restorative_cleaning.ortho_detok_fix(fixed_source, replacements_slang, detoks_slang)
                corrected_target = restorative_cleaning.ortho_detok_fix(fixed_target, replacements_tlang, detoks_tlang)
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
                    continue
                if args.dedup:
                    if args.aggressive_dedup:
                        normalized_src = unidecode(segment["source_segment"].lower().translate(remove_non_alpha))
                        normalized_trg = unidecode(segment["target_segment"].lower().translate(remove_non_alpha))

                        segment_hash = xxh64(normalized_src + "\t" + normalized_trg).hexdigest()

                        charsum = sum(ord(ch) for ch in segment["source_segment"] + segment["target_segment"])
                        ranking = round(charsum / (float(len(segment["source_segment"] + segment["target_segment"]))+0.00001), 2) #the  0.00001 is for the case that length is 0 :D

                    else:
                        segment_hash = xxh64(segment["source_segment"] + "\t" + segment["target_segment"]).hexdigest()
                        ranking = 1
                # if  dedupping: Add extra columnsn with hash and ranking in output file
                # Restored parts object, with the fixed segment, overwritten for each pair of extra segments,
                new_parts = copy.deepcopy(parts)

                new_parts[args.scol - 1] = segment["source_segment"]
                new_parts[args.tcol - 1] = segment["target_segment"]

                if len(segments) > 1:
                    sent_num += 1

                    if args.sdeferredcol and args.tdeferredcol:
                        if "#" in parts[args.sdeferredcol - 1] or "#" in parts[args.tdeferredcol - 1]:
                            # Reconstruction
                            if "#" in parts[args.sdeferredcol - 1]:
                                if sent_num != int(parts[args.sdeferredcol - 1].split('#')[1]):
                                    continue
                            elif "#" in parts[args.tdeferredcol - 1]:
                                if sent_num != int(parts[args.tdeferredcol - 1].split('#')[1]):
                                    continue
                        else:
                            new_parts[args.sdeferredcol - 1] = parts[args.sdeferredcol - 1].rstrip("\n") + "#" + str(sent_num)
                            new_parts[args.tdeferredcol - 1] = parts[args.tdeferredcol - 1].rstrip("\n") + "#" + str(sent_num)
                    if args.sparagraphid and args.tparagraphid:
                        new_parts[args.sparagraphid - 1] = parts[args.sparagraphid - 1].rstrip("\n") + "#" + str(sent_num)
                        new_parts[args.tparagraphid - 1] = parts[args.tparagraphid - 1].rstrip("\n") + "#" + str(sent_num)

                # sentence sides may be empty now because it contained only spaces or similar weird thing
                # for sentences containing only spaces but not normalized, strip them
                if args.ignore_empty or (new_parts[args.scol - 1].strip() and new_parts[args.tcol - 1].strip()):
                    if (args.dedup):
                        # Remove the "/n" at the end of the last item
                        new_parts[-1] = str(new_parts[-1]).strip("\n")

                        new_parts.append(segment_hash)  # hash and ranking are added at the end
                        new_parts.append(ranking)
                        if args.annotated_output:
                            if (new_parts[args.scol - 1] != source_sentence or new_parts[args.tcol - 1] != target_sentence.strip("\n")) :
                                new_parts.append('Yes')
                            else:
                                new_parts.append('No')
                                                        
                        args.output.write("\t".join(str(v) for v in new_parts) + "\n")  # Convert to strings
                        # Remove hash, ranking and bifixed for next iterations of loop
                        new_parts.pop()
                        new_parts.pop()
                        if args.annotated_output:
                            new_parts.pop()
                    else:
                        # When no deduplicating:
                        new_parts[-1] = str(new_parts[-1]).strip("\n")
                        if args.annotated_output:
                            if (new_parts[args.scol - 1] != source_sentence or new_parts[args.tcol - 1] != target_sentence.strip("\n")) :
                                new_parts.append('Yes')
                            else:
                                new_parts.append('No')
                        args.output.write("\t".join(str(v) for v in new_parts) + "\n")
                        if args.annotated_output:
                            new_parts.pop()
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
