#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 03/07/2019 # Initial release # Marta Bañón"
__version__ = "Version 0.2 # 23/08/2019 # Included NLTK segmenter # Marta Bañón"

import signal
import json
import os
import nltk
import sys
import logging

from nltk import load

try:
    from loomchild.segmenter import LoomchildSegmenter
except ImportError:
    pass

class myTimeout(Exception):
    pass

def timeout(signum, frame):
    raise myTimeout

class NLTKSegmenter:
    def __init__(self, lang):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            for i in range(3):
                signal.signal(signal.SIGALRM, timeout)
                signal.alarm(120)
                try:
                    result = nltk.download('punkt', quiet=True)
                    signal.alarm(0)
                    break
                except myTimeout:
                    pass
            else:
                raise Exception("Unable to download 'punkt' NLTK data after 3 retries: try to download it manually or check your internet connection.")

        langname = self.getLanguageName(lang.lower())

        try:
            self.segmenter = load('tokenizers/punkt/{0}.pickle'.format(langname))
        except:
            self.segmenter = load('tokenizers/punkt/english.pickle')

    def get_segmentation(self, sentence):
        sentence_segments = json.loads(json.dumps(self.segmenter.tokenize(sentence)))
        return sentence_segments

    def getLanguageName(self, lang):
        # Returns NLTK *.pickle file for the language, if exists. If not, returns the default (english.pickle)

        if lang == "cs":
            return "czech"

        elif lang == "da":
            return "danish"

        elif lang == "de":
            return "german"

        elif lang == "el":
            return "greek"

        elif lang == "en":
            return "english"

        elif lang == "es":
            return "spanish"

        elif lang == "et":
            return "estonian"

        elif lang == "fi":
            return "finnish"

        elif lang == "fr":
            return "frech"

        elif lang == "it":
            return "italian"

        elif lang == "nb":
            return "norwegian"

        elif lang == "nl":
            return "dutch"

        elif lang == "nn":
            return "norwegian"

        elif lang == "pl":
            return "polish"

        elif lang == "pt":
            return "portuguese"

        elif lang == "ru":
            return "russian"

        elif lang == "sl":
            return "slovene"

        elif lang == "sv":
            return "swedish"

        elif lang == "tr":
            return "turkish"

        else:
            return "english"


class NaiveSegmenter:
    def __init__(self, lang, module="nltk"):
        if module == "loomchild":
            if "loomchild.segmenter" in sys.modules:
                self.segmenter = LoomchildSegmenter(lang)
            else:
                logging.warning("Loomchild segmenter unavailable, falling back to NLTK")
                self.segmenter = NLTKSegmenter(lang)
        elif module == "nltk":
            self.segmenter = NLTKSegmenter(lang)
        else:
            self.segmenter = NLTKSegmenter(lang)

    def __call__(self, sentence):
        return self.segmenter.get_segmentation(sentence)


def naive_segmenter(source_segmenter, target_segmenter, source, target):
    source_segments = source_segmenter(source)
    target_segments = target_segmenter(target)

    if len(source_segments) == len(target_segments):
        segments = []
        for segment_pair in zip(source_segments, target_segments):
            segment = {"source_segment": segment_pair[0], "target_segment": segment_pair[1]}
            segments.append(segment)
        return segments
    else:
        return [{"source_segment": source, "target_segment": target}]
