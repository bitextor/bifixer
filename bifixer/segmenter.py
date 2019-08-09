#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 03/07/2019 # Initial release # Marta Bañón"

from toolwrapper import ToolWrapper

class LoomchildSegmenter(ToolWrapper):
    """A module for interfacing with a Java sentence segmenter. """
    
    def __init__(self,text,lang="en"):
        self.lang = lang
        self.text = text
        program =  "/home/motagirl2/projects/segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:./segment-2.0.2-SNAPSHOT/lib/* net.loomchild.segment.ui.console.Segment"
        argv = ["java", "-cp", program, "-l", self.lang]
        super().__init__(argv)

    def __str__(self):
        return "LoomchildSegmenter(lang=\"{lang}\")".format(lang=self.lang)

    def __call__(self, sentence):
        assert isinstance(sentence, str)
        sentence = sentence.rstrip("\n")
        assert "\n" not in sentence
        if not sentence:
            return []
        self.writeline(sentence)
        return self.readline().split()

def naive_segmenter(source, target, slang, tlang):

    #TO DO: Do this only once, on a setup step    
    source_segmenter = LoomchildSegmenter(slang)
    target_segmenter = LoomchildSegmenter(tlang)

    source_segments = source_segmenter(source)
    target_segments = target_segmenter(target)
    
    print("SOURCE SEGMENTS: " + str(source_segments))
    print("TARGET SEGMENTS: " + str(target_segments))
            
    if len(source_segments) == len(target_segments):
        segments = []
        for segment_pair in zip(source_segments, target_segments):
            segment = {"source_segment": segment_pair.get(0), "target_segment": segment_pair.get(1)}
            segments.append(segment)
        return segments    
    else:            
        return [{"source_segment": source, "target_segment": target}]