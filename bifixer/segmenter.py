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
        argv = ["java", "-cp", program, "-l", self.lang, "-c", self.text]
        super().__init__(argv)

    def __str__(self):
        return "LoomchildSegmenter(text=\"{text}\",lang=\"{lang}\")".format(text=self.text, lang=self.lang)

    def __call__(self, sentence):
        assert isinstance(sentence, str)
#        sentence = sentence.rstrip("\n")
#        assert "\n" not in sentence
        if not sentence:
            return []
        self.writeline(sentence)
        return self.readline().split()

def naive_segmenter(source, target, slang, tlang):
    segments = ToolWrapper(source, slang)
    for s in segments:
        print("SEGMENT: " + s)
    return [{"source_segment": source, "target_segment": target}]