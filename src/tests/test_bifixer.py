#!/usr/bin/env python     

__author__ = "Marta Bañón (mbanon)"
__version__ = "Version 0.1 # 27/08/2019 # Tests for Bifixer # Marta Bañón"
__version__ = "Version 0.2 # 22/06/2021 # Dedup tests # Jaume Zaragoza"

import pytest
# import unittest
import sys
import argparse
import io

sys.path.append('..')

import bifixer
from bifixer import bifixer
from bifixer import restorative_cleaning
from bifixer import segmenter


class TestEmptySpaces():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.scol = 3
    args.tcol = 4
    args.ignore_characters = True
    args.ignore_normalization = True
    args.ignore_orthography = True
    args.ignore_detokenization = True
    args.ignore_segmentation = True
    args.sdeferredcol = None
    args.tdeferredcol = None
    args.sparagraphid = None
    args.tparagraphid = None
    args.header = None
    args.ignore_empty = False
    args.ignore_long = False
    args.input = open("src/tests/input_test_1.txt", "rt")
    args.dedup = False
    args.output = open("src/tests/output_test_1.txt", "w+")
    args.ignore_html = False
    args.annotated_output = False

    def test__empty(self):
        bifixer.fix_sentences(self.args)
        self.args.output.close()

        with open("src/tests/output_expected_1.txt", "rt") as expected, open("src/tests/output_test_1.txt", "rt") as test:
            for e, t in zip(expected, test):
                assert e == t


class TestCharReplacements:
    chars_en, charsRe_en = restorative_cleaning.getCharsReplacements("en")
    chars_ru, charsRe_ru = restorative_cleaning.getCharsReplacements("ru")
    chars_es, charsRe_es = restorative_cleaning.getCharsReplacements("es")
    chars_fr, charsRe_fr = restorative_cleaning.getCharsReplacements("fr")
    chars_el, charsRe_el = restorative_cleaning.getCharsReplacements("el")
    chars_cs, charsRe_cs = restorative_cleaning.getCharsReplacements("cs")
    chars_sl, charsRe_sl = restorative_cleaning.getCharsReplacements("sl")

    punct_en, punctRe_en = restorative_cleaning.getNormalizedPunctReplacements("en")
    punct_ru, punctRe_ru = restorative_cleaning.getNormalizedPunctReplacements("ru")
    punct_es, punctRe_es = restorative_cleaning.getNormalizedPunctReplacements("es")
    punct_fr, punctRe_fr = restorative_cleaning.getNormalizedPunctReplacements("fr")
    punct_el, punctRe_el = restorative_cleaning.getNormalizedPunctReplacements("el")
    punct_cs, punctRe_cs = restorative_cleaning.getNormalizedPunctReplacements("cs")

    def test_mojibake(self):
        correct = "¿La cigüeña bebía café?"
        text_1 = "&#191;La cigüe&#241;a bebía café?"
        text_2 = "Â¿La cigÃ¼eÃ±a bebÃ­a cafÃ©?"
        fixed_1 = restorative_cleaning.fix(text_1, "es", self.chars_es, self.charsRe_es)
        fixed_2 = restorative_cleaning.fix(text_2, "es", self.chars_es, self.charsRe_es)
        assert fixed_1 == correct
        assert fixed_2 == correct

    def test_encoding(self):
        correct_1 = "Brošure"
        text_1 = "BroĹĄure"
        correct_2 = "Možnost polnjenja doma (110-240V) in v avtu (12V). Uporaba za nas... več o tem 3"
        text_2 = "MoĹľnost polnjenja doma (110-240V) in v avtu (12V). Uporaba za nas... veÄŤ o tem 3"
        fixed_1 = restorative_cleaning.fix(text_1, "sl", self.chars_sl, self.charsRe_sl)
        fixed_2 = restorative_cleaning.fix(text_2, "sl", self.chars_sl, self.charsRe_sl)
        assert fixed_1 == correct_1
        assert fixed_2 == correct_2

    def test_wrong_alphabet(self):
        text_1 = "поехали !"
        fixed_1 = restorative_cleaning.normalize(text_1, "ru", self.punct_ru, self.punctRe_ru)
        assert fixed_1 == "поехали!"

        text_2 = "   вАтСн     "  # This contains cyrillic chars!
        fixed_2 = restorative_cleaning.fix(text_2, "en", self.chars_en, self.charsRe_en)
        fixed_2 = restorative_cleaning.normalize(fixed_2, "en", self.punct_es, self.charsRe_es)
        assert fixed_2 == "BATCH"

        text_3 = "Αντικύθηρα"
        fixed_3 = restorative_cleaning.fix(text_3, "el", self.chars_el, self.charsRe_el)
        assert fixed_3 == text_3

        text_4 = "ωοκ"  #Contains greek chars
        fixed_4 = restorative_cleaning.fix(text_4, "en", self.chars_en, self.charsRe_en)
        assert fixed_4 == "wok"

        # Carons: ť
        text_5 = "Iťs me, Mario"
        correct = "It's me, Mario"
        fixed_5 = restorative_cleaning.fix(text_5, "en", self.chars_en, self.charsRe_en)
        fixed_cs = restorative_cleaning.fix(text_5, "cs", self.chars_cs, self.charsRe_cs)
        assert fixed_5 == correct
        assert fixed_cs == text_5

    def test_html_entities(self):
        correct = "¿La cigüeña bebía café?"
        text_1 = "&iquest;La cig&uuml;e&ntilde;a beb&iacute;a caf&eacute;?"
        fixed_1 = restorative_cleaning.fix(text_1, "es", self.chars_es, self.charsRe_es)
        assert fixed_1 == correct

        correct_2 = "This is  a very triccky   sentence  "
        text_2 = "This&#9;is &amp;#13a very&#9triccky&amp;NewLine;\n sentence&amp;#13;&amp;Tab;"
        fixed_2 = restorative_cleaning.fix(text_2, "en", self.chars_en, self.charsRe_en)
        assert fixed_2 == correct_2

    def test_punct(self):
        text_1 = "  Did I pass  the     acid test  ?  "
        correct = "Did I pass the acid test?"
        correct_fr = "Did I pass the acid test ?"
        fixed_1 = restorative_cleaning.fix(text_1, "es", self.chars_es, self.charsRe_es)
        fixed_1 = restorative_cleaning.normalize(fixed_1, "es", self.punct_es, self.punctRe_es)
        fixed_fr = restorative_cleaning.fix(text_1, "fr", self.chars_fr, self.charsRe_fr)
        fixed_fr = restorative_cleaning.normalize(fixed_fr, "fr", self.punct_fr, self.punctRe_fr)
        assert fixed_1 == correct
        assert fixed_fr == correct_fr 

        text_2 = "  {  ¡  Party hard , die young  !   }   "
        correct = "{¡Party hard, die young!}"                        
        fixed_2 = restorative_cleaning.fix(text_2, "en", self.chars_en, self.charsRe_en)
        fixed_en = restorative_cleaning.normalize(fixed_2, "en", self.punct_en, self.punctRe_en)
        assert fixed_en == correct


class TestOrthoFix:
    replacements_en = restorative_cleaning.getReplacements("en")
    replacements_es = restorative_cleaning.getReplacements("es")

    def test_orthography_english(self):
        text_1 = "An abandonned puppy accidentaly faciliated a sucesful wokr"
        correct_1 = "An abandoned puppy accidentally facilitated a successful work"
        fixed_1 = restorative_cleaning.ortho_detok_fix(text_1, self.replacements_en, {})
        assert fixed_1 == correct_1

    def test_orthography_spanish(self):
        text_2 = "Una regilla tipicamente supérflua, sinembargo, apesar de los 25 ºC"
        correct_2 = "Una rejilla típicamente superflua, sin embargo, a pesar de los 25 °C"
        fixed_2 = restorative_cleaning.ortho_detok_fix(text_2, self.replacements_es, {})
        assert fixed_2 == correct_2

class TestDetokFix:
    detoks_mt = restorative_cleaning.getDetokenizations("mt")

    def test_detokenization_maltese(self):
        text_1 = "L - aqwa supplimenti għal taħriġ ta ' intervall ma ' intensità għolja"
        correct_1 = "L-aqwa supplimenti għal taħriġ ta' intervall ma' intensità għolja"
        fixed_1 = restorative_cleaning.ortho_detok_fix(text_1, {}, self.detoks_mt)
        assert fixed_1 == correct_1


class TestSegmenters:
    text_src = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor. Una olla de algo más vaca que carnero, salpicón las más noches, duelos y quebrantos los sábados, lantejas los viernes, algún palomino de añadidura los domingos, consumían las tres partes de su hacienda. El resto della concluían sayo de velarte, calzas de velludo para las fiestas, con sus pantuflos de lo mesmo, y los días de entresemana se honraba con su vellorí de lo más fino. Tenía en su casa una ama que pasaba de los cuarenta, y una sobrina que no llegaba a los veinte, y un mozo de campo y plaza, que así ensillaba el rocín como tomaba la podadera. Frisaba la edad de nuestro hidalgo con los cincuenta años, era de complexión recia, seco de carnes, enjuto de rostro, gran madrugador y amigo de la caza. Quieren decir que tenía el sobrenombre de Quijada, o Quesada, que en esto hay alguna diferencia en los autores que deste caso escriben, aunque, por conjeturas verosímiles, se deja entender que se llamaba Quejana. Pero esto importa poco a nuestro cuento, basta que en la narración dél no se salga un punto de la verdad."
    text_trg = "In a village of La Mancha, the name of which I have no desire to call to mind, there lived not long since one of those gentlemen that keep a lance in the lance-rack, an old buckler, a lean hack, and a greyhound for coursing. An olla of rather more beef than mutton, a salad on most nights, scraps on Saturdays, lentils on Fridays, and a pigeon or so extra on Sundays, made away with three-quarters of his income. The rest of it went in a doublet of fine cloth and velvet breeches and shoes to match for holidays, while on week-days he made a brave figure in his best homespun. He had in his house a housekeeper past forty, a niece under twenty, and a lad for the field and market-place, who used to saddle the hack as well as handle the bill-hook. The age of this gentleman of ours was bordering on fifty, he was of a hardy habit, spare, gaunt-featured, a very early riser and a great sportsman. They will have it his surname was Quixada or Quesada (for here there is some difference of opinion among the authors who write on the subject), although from reasonable conjectures it seems plain that he was called Quexana. This, however, is of but little importance to our tale, it will be enough not to stray a hair’s breadth from the truth in the telling of it."

    def test_NLTK(self):
        segmenter_es = segmenter.NaiveSegmenter("es", "nltk")
        segmenter_en = segmenter.NaiveSegmenter("en", "nltk")

        segments = segmenter.naive_segmenter(segmenter_es, segmenter_en, self.text_src, self.text_trg)

        assert len(segments) == 7

    def test_Loomchild(self, capsys):

        if "loomchild.segmenter" not in sys.modules:
            with capsys.disabled():
                print("\n************** Warning: The optional Loomchild Segmenter is not installed. Skipping test.******************\n")
            return

        segmenter_es = segmenter.NaiveSegmenter("es", "loomchild")
        segmenter_en = segmenter.NaiveSegmenter("en", "loomchild")

        segments = segmenter.naive_segmenter(segmenter_es, segmenter_en, self.text_src, self.text_trg)

        assert len(segments) == 7


class TestDedup:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.scol = 3
    args.tcol = 4
    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_normalization = True
    args.ignore_orthography = True
    args.ignore_detokenization = True
    args.ignore_segmentation = True
    args.ignore_empty = True
    args.ignore_long = True
    args.dedup = True
    args.sdeferredcol = None
    args.tdeferredcol = None
    args.sparagraphid = None
    args.tparagraphid = None
    args.header = None
    args.aggressive_dedup = False
    args.input = open("src/tests/input_test_2.txt", "rt")
    args.output = open("src/tests/output_test_dedup.txt", "w+")
    args.ignore_html = False
    args.annotated_output = False

    def test_aggressive_dedup(self):
        bifixer.fix_sentences(self.args)
        self.args.input.close()
        self.args.output.close()

        with open("src/tests/output_test_dedup.txt") as file_:
            hashes = []
            for line in file_:
                parts = line.rstrip("\n").split("\t")
                hashes.append(parts[4])
            assert hashes[0] == hashes[1]
            assert hashes[1] != hashes[2]
            assert hashes[2] != hashes[3]
            assert hashes[4] != hashes[5]

class TestAggressiveDedup:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.scol = 3
    args.tcol = 4
    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_normalization = True
    args.ignore_orthography = True
    args.ignore_detokenization = True
    args.ignore_segmentation = True
    args.ignore_empty = True
    args.ignore_long = True
    args.dedup = True
    args.sdeferredcol = None
    args.tdeferredcol = None
    args.sparagraphid = None
    args.tparagraphid = None
    args.header = None
    args.aggressive_dedup = True
    args.input = open("src/tests/input_test_2.txt", "rt")
    args.output = open("src/tests/output_test_aggr_dedup.txt", "w+")
    args.ignore_html = False
    args.annotated_output = False

    def test_aggressive_dedup(self):
        bifixer.fix_sentences(self.args)
        self.args.input.close()
        self.args.output.close()

        with open("src/tests/output_test_aggr_dedup.txt") as file_:
            hashes = []
            for line in file_:
                parts = line.rstrip("\n").split("\t")
                hashes.append(parts[4])
            assert hashes[0] == hashes[1]
            assert hashes[1] == hashes[2]
            assert hashes[2] == hashes[3]
            assert hashes[4] == hashes[5]

'''
class TestMulti:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    args.srclang = "en"
    args.trglang = "es"
    args.ignore_characters = True
    args.ignore_orthography = True
    args.ignore_segmentation = True
    args.ignore_empty = False
    args.ignore_long = False
'''
# if __name__ == "__main__":
#    unittest.main()
