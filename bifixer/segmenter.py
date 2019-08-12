#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 03/07/2019 # Initial release # Marta Bañón"

import json
from toolwrapper import ToolWrapper


class LoomchildSegmenter(ToolWrapper):
    """A module for interfacing with a Java sentence segmenter. """
    
    def __init__(self,lang="en"):
        self.lang = lang
        program =  "/home/motagirl2/projects/segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:/home/motagirl2/projects/segment/segment-ui/target/segment-2.0.2-SNAPSHOT/lib/* net.loomchild.segment.ui.console.Segment"
#        argv = ["/user/bin/java", "-cp", "/home/mbanon/project/segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:/home/mbanon/project/segment/segment-ui/target/segment-2.0.2-SNAPSHOT/lib/*", "net.loomchild.segment.ui.console.Segment",  "-c"]
#        argv = ["/usr/bin/rev"]
        argv = ["java", "-cp",  "/home/motagirl2/projects/segment/segment-ui/target/segment-ui-2.0.2-SNAPSHOT.jar:/home/motagirl2/projects/segment/segment-ui/target/segment-2.0.2-SNAPSHOT/lib/*", "net.loomchild.segment.ui.console.Segment", "-c"]
        
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

def naive_segmenter(source, target, slang, tlang):

    #TO DO: Do this only once, on a setup step    
    source_segmenter = LoomchildSegmenter(slang)
    target_segmenter = LoomchildSegmenter(tlang)

    source_segments = json.loads(source_segmenter(source))
    target_segments = json.loads(target_segmenter(target))
     
            
    if len(source_segments) == len(target_segments):
        segments = []
        for segment_pair in zip(source_segments, target_segments):
            segment = {"source_segment": segment_pair[0], "target_segment": segment_pair[1]}
            segments.append(segment)
        return segments    
    else:            
        return [{"source_segment": source, "target_segment": target}]