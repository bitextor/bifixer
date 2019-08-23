#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 03/07/2019 # Initial release # Marta Bañón"

import json
import os

from toolwrapper import ToolWrapper


class LoomchildSegmenter(ToolWrapper):
    """A module for interfacing with a Java sentence segmenter. """
    
    def __init__(self,lang="en"):
        curpath = os.path.dirname(os.path.abspath(__file__))+"/"
        self.lang = lang
        self.rules = self.getBestRules(lang)        

        if self.rules != "DEFAULT":    
            argv = ["java", "-cp",  curpath+"../segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:"+curpath+"../segment/segment-ui/target/segment-2.0.2-SNAPSHOT/lib/*", "net.loomchild.segment.ui.console.Segment", "-l", self.lang, "-s", curpath+"../segment/srx/"+self.rules, "-c"]
        else:            
            argv = ["java", "-cp",  curpath+"../segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:"+curpath+"../segment/segment-ui/target/segment-2.0.2-SNAPSHOT/lib/*", "net.loomchild.segment.ui.console.Segment", "-l", lang,"-c"]

        super().__init__(argv)
        

    def __str__(self):
        return "LoomchildSegmenter()".format()

    def __call__(self, sentence):
        assert isinstance(sentence, str)
        sentence = sentence.rstrip("\n")
        assert "\n" not in sentence
        if not sentence:
            return []
        self.writeline(sentence)

        return self.readline()
        
    def getBestRules(self, lang):
        #Based on benchmarks: https://docs.google.com/spreadsheets/d/1mGJ9MSyMlsK0EUDRC2J50uxApiti3ggnlrzAWn8rkMg/edit?usp=sharing
        
        omegaTLangs = ["bg", "cs", "sl", "sv"]
        ptdrLangs = ["el", "et", "fi", "hr", "hu", "lt", "lv"]
        nonAggressiveLangs = ["es", "it", "nb", "nn"]
        languageToolLangs = ["da", "de", "en", "fr", "nl", "pl", "pt", "ro", "sk", "sr", "uk"]

        if lang in omegaTLangs:
            return "OmegaT.srx"
        elif lang in ptdrLangs:
            return "PTDR.srx"
        elif lang in nonAggressiveLangs:
            return "NonAggressive.srx"
        elif lang in languageToolLangs:
            return "language_tools.segment.srx"
        else:
            return "DEFAULT"
                
class  NaiveSegmenter:
    def __init__(self, lang):
        self.segmenter = LoomchildSegmenter(lang)
        
    def __call__(self, sentence):
        return get_segmentation(sentence)

    def get_segmentation(self, sentence):
        sentence_segments = json.loads(self.segmenter(sentence))
        return sentence_segments

#class NLTKSegmenter():
#    def __init__(self, lang):
#        return 
    
def naive_segmenter(source_segmenter, target_segmenter, source, target):
    source_segments = source_segmenter.get_segmentation(source)
    target_segments = target_segmenter.get_segmentation(target)   

    if len(source_segments) == len(target_segments):
        segments = []
        for segment_pair in zip(source_segments, target_segments):
            segment = {"source_segment": segment_pair[0], "target_segment": segment_pair[1]}
            segments.append(segment)
        return segments    
    else:            
        return [{"source_segment": source, "target_segment": target}]