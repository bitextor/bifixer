#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 27/08/2019 # Tests for Bifixer # Marta Bañón"


import pytest
#import unittest
import sys
import argparse
import io


sys.path.append('..')

import bifixer
from bifixer import bifixer
from bifixer import restorative_cleaning

class TestEmptySpaces():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.scol = 3
    args.tcol = 4
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False
    args.input = open("input_test_1.txt", "rt")
    args.dedup = False
    args.output = open("output_test_1.txt", "w+")            

    def test__empty(self):   
        bifixer.fix_sentences(self.args)
        self.args.output.close()                

        with open("output_expected_1.txt", "rt") as expected, open("output_test_1.txt", "rt") as test:
            for e,t in zip(expected, test):                        
                assert e == t


class TestCharReplacements:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    chars_en, charsRe_en = restorative_cleaning.getCharsReplacements("en")
    chars_ru, charsRe_ru = restorative_cleaning.getCharsReplacements("ru")
    chars_es, charsRe_es = restorative_cleaning.getCharsReplacements("es")

    punct_en, punctRe_en = restorative_cleaning.getNormalizedPunctReplacements("en")
    punct_ru, punctRe_ru = restorative_cleaning.getNormalizedPunctReplacements("ru")
    punct_es, punctRe_es = restorative_cleaning.getNormalizedPunctReplacements("es")

    def test_mojibake(self):
        correct = "¿La cigüeña bebía café?"
        text_1 ="&#191;La cigüe&#241;a bebía café?"
        text_2 = "Â¿La cigÃ¼eÃ±a bebÃ­a cafÃ©?"
        fixed_1 = restorative_cleaning.fix(text_1, "es", self.chars_es, self.charsRe_es, self.punct_es, self.punctRe_es)
        fixed_2 = restorative_cleaning.fix(text_2, "es", self.chars_es, self.charsRe_es, self.punct_es, self.punctRe_es)
        assert fixed_1 == correct
        assert fixed_2 == correct

    
    def test_wrong_alphabet(self):
        text_1 = "поехали !"    
        fixed_1 = restorative_cleaning.fix(text_1, "ru", self.chars_ru, self.charsRe_ru, self.punct_ru, self.punctRe_ru)
        assert fixed_1 == "поехали!"
        
        text_2 = "   вАтСн     " #This contains cyrillic chars!
        fixed_2 = restorative_cleaning.fix(text_2, "en", self.chars_en, self.charsRe_en, self.punct_en, self.punctRe_en)
        assert fixed_2 == "BATCH"
        
        
    def test_html_entities(self):
        correct = "¿La cigüeña bebía café?"
        text_1 = "&iquest;La cig&uuml;e&ntilde;a beb&iacute;a caf&eacute;?"
        fixed_1 =  restorative_cleaning.fix(text_1, "es", self.chars_es, self.charsRe_es, self.punct_es, self.punctRe_es)
        assert fixed_1 == correct
        

        
    
'''
class TestPunctReplacements:

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False

    punctChars_slang, punctRe_slang = restorative_cleaning.getNormalizedPunctReplacements(args.srclang)
    punctChars_tlang, punctRe_tlang = restorative_cleaning.getNormalizedPunctReplacements(args.trglang)
        
    def test_multi_space:
    
    def test_punct_french:
    
    def test_punct:
    
class TestOrthoFix:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False

    
    def test_orthography_danish:
    
    def test_orthography_english:
    
    def test_orthography_spanish:
    
    
class TestNLTKSegmenter:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False


class TestLoomchildSegmenter:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False


class TestDedup:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False

class TestAggressiveDedup:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False

class TestMulti:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False
'''
#if __name__ == "__main__":
#    unittest.main()