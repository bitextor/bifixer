#!/usr/bin/env python
import ftfy
import os
import regex
import re
import html

global_chars_lang = {}


def getCharsReplacements(lang):
    # languages that use cyrillic alphabet
    # Check https://www.tug.org/TUGboat/tb17-2/tb51pisk.pdf and/or
    # https://www.quora.com/Which-languages-are-written-in-Cyrillic-script
    # for a comprehensive list
    # Some of the langs does accept both cyrillic and latin, or is migrating to latin
    cyrillic_langs = [
        "ab",  # abkhazian
        "av",  # avar/avaric
        "az",  # azerbaijani
        "ba",  # bashkir
        "be",  # belarusian
        "bg",  # bulgarian
        "bs",  # bosnian
        "ce",  # chechen
        "cv",  # chuvash
        "kk",  # kazakh
        "ku",  # kurdish
        "kv",  # komi
        "ky",  # kirghiz/kyrgyz
        "mk",  # macedonian
        "mn",  # mongolian
        "os",  # ossetic/ossetian
        "ru",  # russian
        "sr",  # serbian
        "tg",  # tajik/tadzhik
        "tk",  # turkmen
        "tt",  # tatar
        "ug",  # uighur
        "uk",  # ukranian
        "uz"  # uzbek
    ]

    # https://en.wikipedia.org/wiki/Caron
    # http://diacritics.typo.cz/index.php?id=5
    langs_with_carons = [
        "cs",  # czech
        "et",  # estonian
        "fi",  # finnish
        "hr",  # croatian
        "ln",  # lingala
        "lt",  # lithuanian
        "lv",  # latvian
        "sk",  # slovak
        "sl",  # slovenian
        "sr",  # serbian
        "yo"  # yoruba
    ]

    # Annoying characters, common for all languages
    chars = {
        '\u2028': ' ',  # line separators (\n)
        '&#10;': "",  # \n
        '\n': "",
        '&#xa': "",
        '&#xA': "",

        '\u000D': "",  # carriage returns (\r)
        '&#13;': " ",
        '&#xd;': " ",
        '&#xD;': " ",

        # unicode ligatures
        '\uFB00': 'ff',
        '\uFB01': 'fi',
        '\uFB02': 'fl',
        '\uFB03': 'ffi',
        '\uFB04': 'ffl',
        '\uFB06': 'st',

        '&nbsp;': " ",
        '&lt;': "<",
        '&gt;': ">",
        '&amp;': "&",
        '&quot;': '"',
        '&apos;': "'",
        '&iexcl;': '¡',
        '&cent;': '¢',
        '&pound;': '£',

        '&Agrave;': 'À',
        '&Aacute;': 'Á',
        '&Acirc;': 'Â',
        '&Atilde;': 'Ã',
        '&Auml;': 'Ä',
        '&Aring;': 'Å',
        '&Aelig;': 'Æ',

        '&agrave;': 'à',
        '&aacute;': 'á',
        '&acirc;': 'â',
        '&atilde;': 'ã',
        '&auml;': 'ä',
        '&aring;': 'å',
        '&aelig;': 'æ',

        '&Ccedil;': 'Ç',
        '&ccedil;': 'ç',

        '&Egrave;': 'È',
        '&Eacute;': 'É',
        '&Ecirc;': 'Ê',
        '&Euml;': 'Ë',

        '&egrave;': 'è',
        '&eacute;': 'é',
        '&ecirc;': 'ê',
        '&euml;': 'ë',
        '&Igrave;': 'Ì',
        '&Iacute;': 'Í',
        '&Icirc;': 'Î',
        '&Iuml;': 'Ï',

        '&igrave;': 'ì',
        '&iacute;': 'í',
        '&icirc;': 'î',
        '&iuml;': 'ï',

        '&Ntilde;': 'Ñ',
        '&ntilde;': 'ñ',

        '&Ograve;': 'Ò',
        '&Oacute;': 'Ó',
        '&Ocirc;': 'Ô',
        '&Otilde;': 'Õ',
        '&Ouml;': 'Ö',

        '&ograve;': 'ò',
        '&oacute;': 'ó',
        '&ocirc;': 'ô',
        '&otilde;': 'õ',
        '&ouml;': 'ö',

        '&times;': '×',  # ×
        '&Oslash;': '',  # Ø
        '&oslash;': '',  # ø

        '&Ugrave;': 'Ù',
        '&Uacute;': 'Ú',
        '&Ucirc;': 'Û',
        '&Uuml;': 'Ü',

        '&ugrave;': 'ù',
        '&uacute;': 'ú',
        '&ucirc;': 'û',
        '&uuml;': 'ü',

        '&Yacute;': 'Ý',
        '&yacute;': 'ý',
        '&yuml;': 'ÿ',  # ÿ
        '&Yuml;': 'Ÿ',  # capital Y with diaeres Ÿ

        '&thorn;': 'Þ',  # þ
        '&szlig;': 'ß',  # ß

        '&divide;': '÷',  # ÷
        '&euro;': '€',

        '\u02C1': "¿",  # ˁ -> ?
        '\u02C2': "<",  # ˂ -> <
        '\u02C3': ">",  # ˃ -> >

        # https://www.utf8-chartable.de/unicode-utf8-table.pl?number=1024&names=2&utf8=char

        'Â¿': '¿',
        'Â¡': '¡',

        'Ã€': 'À',
        'Ã<80>': 'À',
        'Ã<81>': 'Á',
        'Ã<82>': 'Â',
        'Ã<83>': 'Ã',
        'Ã<84>': 'Ä',
        'Ã<85>': 'Å',
        'Ã‚': 'Â',
        'Ãƒ': 'Ã',
        'Ã„': 'Ä',
        'Ã…': 'Å',
        'Ã<86>': 'Æ',
        'Ã†': 'Æ',
        'Ä<80>': 'Ā',
        'Ä<82>': 'Ă',

        'Ã¡': 'á',
        'Ã¤': 'ä',
        'Ã¢': 'â',
        'Ã£': 'ã',
        'Ã¥': 'å',
        'Ã¦': 'æ',
        'Ä<81>': 'ā',
        'Ä<83>': 'ă',

        'Ã<87>': 'Ç',
        'Ã‡': 'Ç',
        'Ã§': 'ç',

        'Ã<88>': 'È',
        'Ã<89>': 'É',
        'Ã<8A>': 'Ê',
        'Ã<8B>': 'Ë',
        'Ãˆ': 'È',
        'Ã‰': 'É',
        'ÃŠ': 'Ê',
        'Ã‹': 'Ë',

        'Ã¨': 'è',
        'Ã©': 'é',
        'Ãª': 'ê',
        'Ã«': 'ë',

        'Ã<8C>': 'Ì',
        'Ã<8E>': 'Î',
        'ÃŒ': 'Ì',
        'Ã<8D>': 'Í',
        'ÃŽ': 'Î',
        'Ã<8F>': 'Ï',
        'Ã¬': 'ì',
        'Ã<AD>': 'í',
        'Ã®': 'î',
        'Ã¯': 'ï',

        'Ä¾': 'ľ',

        'Ã’': 'Ò',
        'Ã<92>': 'Ò',
        'Ã<93>': 'Ó',
        'Ã<94>': 'Ô',
        'Ã<95>': 'Õ',
        'Ã<96>': 'Ö',
        'Ã“': 'Ó',
        'Ã”': 'Ô',
        'Ã•': 'Õ',
        'Ã–': 'Ö',
        'Ã˜': 'Ø',
        'Ã<98>': 'Ø',
        'Å’': 'Œ',

        'Ã²': 'ò',
        'Ã³': 'ó',
        'Ã´': 'ô',
        'Ãµ': 'õ',
        'Ã¸': 'ø',
        'Å“': 'œ',
        'Ã¶': 'ö',

        'Ã‘': 'Ñ',
        'Ã<91>': 'Ñ',
        'Ã±': 'ñ',

        'Å¡': 'š',

        'Å¥': 'ť',

        'Ã<99>': 'Ù',
        'Ã<9A>': 'Ú',
        'Ã<9B>': 'Û',
        'Ã<9C>': 'Ü',
        'Ã™': 'Ù',
        'Ãš': 'Ú',
        'Ã›': 'Û',
        'Ãœ': 'Ü',

        'Ã¹': 'ù',
        'Ãº': 'ú',
        'Ã¼': 'ü',
        'Ã»': 'û',

        'Ã<9D>': 'Ý',
        'Å¸': 'Ÿ',

        'Ã½': 'ý',
        'Ã¿': 'ÿ',
        'Å½': 'Ž',
        'Å¾': 'ž',

        'Ãž': 'Þ',
        'Ã<9E>': 'Þ',
        'Ã¾': 'þ',

        'Ã<90>': 'Ð',
        'ÃŸ': 'ß',
        'Ã<9F>': 'ß',
        'Âµ': 'µ',
        'Ã°': 'ð'

    }

    if lang.lower() not in langs_with_carons:
        chars['\u0165'] = "t'"  # latin small letter t with caron ť
        chars['\u0192'] = "f"  # latin small letter f with hook ƒ

    if lang.lower() not in cyrillic_langs:
        # Cyrilic charcaters replaced to latin characters
        chars['Ѐ'] = 'È'
        chars['Ё'] = 'Ë'
        chars['Ѕ'] = 'S'
        chars['Ї'] = 'Ï'
        chars['І'] = 'I'
        chars['Ј'] = 'J'
        chars['А'] = 'A'
        chars['В'] = 'B'
        chars['Е'] = 'E'
        chars['К'] = 'K'
        chars['М'] = 'M'
        chars['Н'] = 'H'
        chars['О'] = 'O'
        chars['Р'] = 'P'
        chars['С'] = 'C'
        chars['Т'] = 'T'
        chars['У'] = 'y'
        chars['Х'] = 'X'
        chars['Ь'] = 'b'
        chars['ѐ'] = 'è'
        chars['ё'] = 'ë'
        chars['а'] = 'a'
        chars['в'] = 'B'
        chars['г'] = 'r'
        chars['е'] = 'e'
        chars['к'] = 'k'
        chars['м'] = 'M'
        chars['н'] = 'H'
        chars['о'] = 'o'
        chars['р'] = 'p'
        chars['с'] = 'c'
        chars['т'] = 'T'
        chars['у'] = 'y'
        chars['х'] = 'x'
        chars['ь'] = 'b'
        chars['ѕ'] = 's'
        chars['і'] = 'i'
        chars['ї'] = 'ï'
        chars['ј'] = 'j'
        chars['Ү'] = 'Y'
        chars['Ү'] = 'Y'
        chars['Һ'] = 'h'
        chars['һ'] = 'h'
        chars['Ӏ'] = 'I'
        chars['ӏ'] = 'I'
        chars['Ӓ'] = 'Ä'
        chars['ӓ'] = 'ä'
        chars['Ԁ'] = 'd'
        chars['ԁ'] = 'd'
        chars['Ԛ'] = 'Q'
        chars['ԛ'] = 'q'
        chars['Ԝ'] = 'W'
        chars['ԝ'] = 'w'
        chars['Ꙇ'] = 'l'
        chars['ꙇ'] = 'l'
        chars['Ꚃ'] = 'S'
        chars['ꚃ'] = 'S'
        chars['\u0443'] = 'y'  #

    if lang.lower() == "de":
        # Remove and/or replace certain keys from 'chars' in German
        chars['&bdquo;'] = '„'
        chars['\u201E'] = '„'
        chars['\u00D8'] = 'Ø'  # latin capital letter o with stroke Ø
        chars['\u00F8'] = 'ø'  # latin small letter o with stroke ø
        chars['&Oslash;'] = 'Ø'  # Ø
        chars['&oslash;'] = 'ø'
    else:
        chars['׳'] = "'"
        chars['״'] = '"'
        chars['־'] = '-'
        chars['׀'] = '|'
        chars['׃'] = ':'

    if lang.lower() != "el":
        # Greek Letters
        chars['&Alpha;'] = 'A'  # Alpha   Α -> Changed to latin A
        chars['Α'] = 'A'  # Alpha  Α -> Changed to latin A
        chars['&Beta;'] = 'B'  # Beta     Β -> Changed to latin B
        chars['Β'] = 'B'  # Beta   Β -> Changed to latin B
        chars['&Gamma;'] = 'Γ'  # Gamma   Γ
        chars['&Delta;'] = 'Δ'  # Delta   Δ
        chars['&Epsilon;'] = 'E'  # Epsilon       Ε -> Changed to latin E
        chars['Ε'] = 'E'  # Epsilon        Ε -> Changed to latin E
        chars['&Zeta;'] = 'Z'  # Zeta     Ζ -> Changed to latin Z
        chars['Ζ'] = 'Z'  # Zeta   Ζ -> Changed to latin Z
        chars['&Eta;'] = 'H'  # Eta       Η -> Changed to latin H
        chars['Η'] = 'H'  # Eta    Η -> Changed to latin H
        chars['&Theta;'] = 'Θ'  # Theta   Θ
        chars['&Iota;'] = 'I'  # Iota     Ι -> Chaged to latin I
        chars['Ι'] = 'I'  # Iota   Ι -> Chaged to latin I
        chars['&Kappa;'] = 'K'  # Kappa   Κ -> Changed to latin K
        chars['Κ'] = 'K'  # Kappa  Κ -> Changed to latin K
        chars['&Lambda;'] = 'Λ'  # Lambda Λ
        chars['&Mu;'] = 'M'  # Mu Μ -> Changed to latin M
        chars['Μ'] = 'M'  # Mu     Μ -> Changed to latin M
        chars['&Nu;'] = 'N'  # Nu Ν -> Changed to latin N
        chars['Ν'] = 'N'  # Nu     Ν -> Changed to latin N
        chars['&Xi;'] = 'Ξ'  # Xi Ξ
        chars['&Omicron;'] = 'O'  # Omicron       Ο -> Changed to latin O
        chars['Ο'] = 'O'  # Omicron        Ο -> Changed to latin O
        chars['&Pi;'] = 'Π'  # Pi Π
        chars['&Rho;'] = 'P'  # Rho       Ρ -> Changed to latin P
        chars['Ρ'] = 'P'  # Rho    Ρ -> Changed to latin P
        chars['&Sigma;'] = 'Σ'  # Sigma   Σ
        chars['&Tau;'] = 'T'  # Tau       Τ -> Changed to latin T
        chars['Τ'] = 'T'  # Tau    Τ -> Changed to latin T
        chars['&Upsilon;'] = 'Y'  # Upsilon       Υ -> Changed to latin Y
        chars['Υ'] = 'Y'  # Upsilon        Υ -> Changed to latin Y
        chars['&Phi;'] = 'Φ'  # Phi       Φ
        chars['&Chi;'] = 'X'  # Chi       Χ -> Changed to latin X
        chars['Χ'] = 'X'  # Chi    Χ -> Changed to latin X
        chars['&Psi;'] = 'Ψ'  # Psi       Ψ
        chars['&Omega;'] = 'Ω'  # Omega   Ω
        chars['&alpha;'] = 'a'  # alpha   α -> Changed to latin a
        chars['α'] = 'a'  # alpha  α -> Changed to latin a
        chars['&beta;'] = 'β'  # beta     β
        chars['&gamma;'] = 'γ'  # gamma   γ
        chars['&delta;'] = 'δ'  # delta   δ
        chars['&epsilon;'] = 'ε'  # epsilon       ε
        chars['&zeta;'] = 'ζ'  # zeta     ζ
        chars['&eta;'] = 'n'  # eta       η -> Changed to latin n
        chars['η'] = 'n'  # eta    η -> Changed to latin n
        chars['&theta;'] = 'θ'  # theta   θ
        chars['&iota;'] = 'ι'  # iota     ι
        chars['&kappa;'] = 'k'  # kappa   κ -> Changed to latin k
        chars['κ'] = 'k'  # kappa  κ -> Changed to latin k
        chars['&lambda;'] = 'λ'  # lambda λ
        chars['&mu;'] = 'μ'  # mu μ
        chars['&nu;'] = 'v'  # nu ν -> Changed to latin v
        chars['ν'] = 'v'  # nu     ν -> Changed to latin v
        chars['&xi;'] = 'ξ'  # xi ξ
        chars['&omicron;'] = 'o'  # omicron       ο -> Changed to latin o
        chars['ο'] = 'o'  # omicron        ο -> Changed to latin o
        chars['&pi;'] = 'π'  # pi π
        chars['&rho;'] = 'p'  # rho       ρ -> Changed to latin p
        chars['ρ'] = 'p'  # rho    ρ -> Changed to latin p
        chars['&sigmaf;'] = 'ς'  # sigmaf ς
        chars['&sigma;'] = 'σ'  # sigma   σ
        chars['&tau;'] = 't'  # tau       τ -> Changed to latin t
        chars['τ'] = 't'  # tau    τ -> Changed to latin t
        chars['&upsilon;'] = 'u'  # upsilon       υ -> Changed to latin u
        chars['υ'] = 'u'  # upsilon        υ -> Changed to latin u
        chars['&phi;'] = 'φ'  # phi       φ
        chars['&chi;'] = 'χ'  # chi       χ
        chars['&psi;'] = 'ψ'  # psi       ψ
        chars['&omega;'] = 'ω'  # omega   ω
        chars['&thetasym;'] = 'ϑ'  # theta symbol ϑ
        chars['&upsih;'] = 'ϒ'  # upsilon symbol  ϒ
        chars['&piv;'] = 'ϖ'  # pi symbol ϖ
        chars['\u03BF'] = 'o'  # GREEK SMALL LETTER OMICRON
    else:
        # Greek Letters
        chars['&Alpha;'] = 'Α'  # Alpha
        chars['&Beta;'] = 'Β'  # Beta
        chars['&Gamma;'] = 'Γ'  # Gamma   Γ
        chars['&Delta;'] = 'Δ'  # Delta   Δ
        chars['&Epsilon;'] = 'Ε'  # Epsilon
        chars['&Zeta;'] = 'Ζ'  # Zeta
        chars['&Eta;'] = 'Η'  # Eta
        chars['&Theta;'] = 'Θ'  # Theta   Θ
        chars['&Iota;'] = 'Ι'  # Iota
        chars['&Kappa;'] = 'Κ'  # Kappa
        chars['&Lambda;'] = 'Λ'  # Lambda Λ
        chars['&Mu;'] = 'Μ'  # Mu
        chars['&Nu;'] = 'Ν'  # Nu
        chars['&Xi;'] = 'Ξ'  # Xi
        chars['&Omicron;'] = 'Ο'  # Omicron
        chars['&Pi;'] = 'Π'  # Pi Π
        chars['&Rho;'] = 'Ρ'  # Rho
        chars['&Sigma;'] = 'Σ'  # Sigma   Σ
        chars['&Tau;'] = 'Τ'  # Tau
        chars['&Upsilon;'] = 'Υ'  # Upsilon
        chars['&Phi;'] = 'Φ'  # Phi       Φ
        chars['&Chi;'] = 'Χ'  # Chi
        chars['&Psi;'] = 'Ψ'  # Psi       Ψ
        chars['&Omega;'] = 'Ω'  # Omega   Ω
        chars['&alpha;'] = 'α'  # alpha   α
        chars['&beta;'] = 'β'  # beta     β
        chars['&gamma;'] = 'γ'  # gamma   γ
        chars['&delta;'] = 'δ'  # delta   δ
        chars['&epsilon;'] = 'ε'  # epsilon       ε
        chars['&zeta;'] = 'ζ'  # zeta     ζ
        chars['&eta;'] = 'η'  # eta       η
        chars['&theta;'] = 'θ'  # theta   θ
        chars['&iota;'] = 'ι'  # iota     ι
        chars['&kappa;'] = 'κ'  # kappa   κ
        chars['&lambda;'] = 'λ'  # lambda λ
        chars['&mu;'] = 'μ'  # mu μ
        chars['&nu;'] = 'ν'  # nu ν
        chars['&xi;'] = 'ξ'  # xi ξ
        chars['&omicron;'] = 'ο'  # omicron       ο
        chars['&pi;'] = 'π'  # pi π
        chars['&rho;'] = 'ρ'  # rho       ρ
        chars['&sigmaf;'] = 'ς'  # sigmaf ς
        chars['&sigma;'] = 'σ'  # sigma   σ
        chars['&tau;'] = 'τ'  # tau       τ
        chars['&upsilon;'] = 'υ'  # upsilon       υ
        chars['&phi;'] = 'φ'  # phi       φ
        chars['&chi;'] = 'χ'  # chi       χ
        chars['&psi;'] = 'ψ'  # psi       ψ
        chars['&omega;'] = 'ω'  # omega   ω
        chars['&thetasym;'] = 'ϑ'  # theta symbol ϑ
        chars['&upsih;'] = 'ϒ'  # upsilon symbol  ϒ
        chars['&piv;'] = 'ϖ'  # pi symbol ϖ
        chars['\u03BF'] = 'ο'  # GREEK SMALL LETTER OMICRON

    if lang.lower() != "ja":
        chars['\uFF5B'] = '{'  # ｛
        chars['\uFF5D'] = '}'  # ｝
        chars['\uFF08'] = '('  # （
        chars['\uFF09'] = ')'  # ）
        chars['\uFF3B'] = '['  # ［
        chars['\uFF3D'] = ']'  # ］
        chars['\u3010'] = '('  # 【
        chars['\u3011'] = ')'  # 】
        chars['\u3002'] = '.'  # 。
        chars['\u3001'] = ','  # 、
        chars['\uFF0C'] = ','  # ，
        chars['\uFF1A'] = ':'  # ：
        chars['\uFF1B'] = ';'  # ；
        chars['\uFF1F'] = '?'  # ？
        chars['\uFF01'] = '!'  # ！
        chars['\uFF1C'] = '<'  # ＜
        chars['\uFF1D'] = '='  # ＝
        chars['\uFF1E'] = '>'  # ＞
        chars['\uFF3F'] = '_'  # ＿
        chars['\uFF40'] = "'"  # ｀
    else:
        chars['{'] = '\uFF5B'  # ｛
        chars['}'] = '\uFF5D'  # ｝
        chars['('] = '\uFF08'  # （
        chars[')'] = '\uFF09'  # ）
        chars['['] = '\uFF3B'  # ［
        chars[']'] = '\uFF3D'  # ］
        chars['\u3010'] = '\u3010'  # 【 -  #We maintain the same char
        chars['\u3011'] = '\u3011'  # 】 -  #We maintain the same char
        chars['\u3002'] = '\u3002'  # 。 #We maintain the same char
        chars[','] = '\u3001'  # 、
        chars[','] = '\uFF0C'  # ，
        chars['\u2026'] = '\u2026'  # … #We maintain the same char
        chars['\u2025'] = '\u2025'  # ‥ #We maintain the same char
        chars[':'] = '\uFF1A'  # ：
        chars[';'] = '\uFF1B'  # ；
        chars['?'] = '\uFF1F'  # ？
        chars['!'] = '\uFF01'  # ！
        chars['<'] = '\uFF1C'  # ＜
        chars['='] = '\uFF1D'  # ＝
        chars['>'] = '\uFF1E'  # ＞
        chars['_'] = '\uFF3F'  # ＿
        chars["'"] = '\uFF40'  # ｀

    charsRe = re.compile("(\\" + '|\\'.join(chars.keys()) + ")")

    return chars, charsRe


def getNormalizedPunctReplacements(lang):
    if lang.lower() == "fr":
        replacements = {
            " ,": ",",
            " )": ")",
            " }": "}",
            " ]": "]",
            #            " \""      :       "\"",          
            " ...": "...",

            "( ": "(",
            "{ ": "{",
            "[ ": "["
        }

    else:
        replacements = {
            " !": "!",
            " ?": "?",
            " :": ":",
            " ;": ";",
            " ,": ",",
            " )": ")",
            " }": "}",
            " ]": "]",
            #            " \""	:	"\"",
            " ...": "...",
            " º": "º",

            "( ": "(",
            "{ ": "{",
            "[ ": "[",
            "¿ ": "¿",
            "¡ ": "¡"
        }
    rep = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(rep.keys()))
    return rep, pattern


# Orthographic corrections
def getReplacements(lang):
    replacements = {}
    input_replacements = None

    if lang.lower() in ["da", "de", "en", "es", "nb", "nl", "pt", "tr"]:
        input_replacements = open(os.path.dirname(os.path.realpath(__file__)) + "/replacements/replacements." + lang.lower(), "r")

    if input_replacements is not None:
        for i in input_replacements:
            field = i.split(u"\t")
            replacements[field[0].strip()] = field[1].strip()

    return replacements


def replace_chars(match):
    global global_chars_lang
    char = match.group(0)
    return global_chars_lang[char]


def replace_chars3(match):
    char = match.group(0)
    return ""


def fix(text, lang, chars_rep, chars_pattern, punct_rep, punct_pattern):
    global global_chars_lang
    global_chars_lang = chars_rep

    # htmlEntity=regex.compile(r'[&][[:space:]]*[#][[:space:]]*[0-9]{2,4}[[:space:]]*[;]?',regex.U)
    chars3Re = regex.compile("[\uE000-\uFFFF]")
    chars3Re2 = regex.compile("[\u2000-\u200F]")
    chars3Re3 = regex.compile("\u007F|[\u0080-\u00A0]")
    quotesRegex = regex.compile("(?P<start>[[:alpha:]])\'\'(?P<end>(s|S|t|T|m|M|d|D|re|RE|ll|LL|ve|VE|em|EM)\W)")
    collapse_spaced_entities = regex.compile('([&][ ]*[#][ ]*)([0-9]{2,6})([ ]*[;])')

    # Test encode: fix mojibake
    ftfy_fixed_text = " ".join([ftfy.fix_text_segment(word, uncurl_quotes=False, fix_latin_ligatures=False) for word in text.split()])
    # ftfy_fixed_text= ftfy.fix_text_segment(stripped_text, fix_entities=True,uncurl_quotes=False,fix_latin_ligatures=False)

    # nicely_encoded_text = htmlEntity.sub(html.unescape, nicely_encoded_text)
    nicely_encoded_text = html.unescape(ftfy_fixed_text)

    # First replacing all HTML entities
    # for substring in htmlEntity.findall(nicely_encoded_text):
    #    code=substring.replace(' ','')[2:].replace(';','')
    #    try:
    #        newChar=chr(int(code))
    #    except ValueError:
    #        newChar=code    
    #    if newChar != "\n":
    #        nicely_encoded_text = nicely_encoded_text.replace(substring,newChar)

    normalized_text = chars_pattern.sub(replace_chars, nicely_encoded_text)

    if lang.lower() != "ja":
        normalized_text = chars3Re.sub(replace_chars3, normalized_text)
    normalized_text = chars3Re2.sub(replace_chars3, normalized_text)
    normalized_text = chars3Re3.sub(replace_chars3, normalized_text)
    normalized_text = quotesRegex.sub("\g<start>\'\g<end>", normalized_text)
    normalized_text_with_normalized_punct = punct_pattern.sub(lambda m: punct_rep[re.escape(m.group(0))], normalized_text)

    collapsed_spaces = re.sub('\s+', ' ', normalized_text_with_normalized_punct)  # Collapse multiple spaces
    collapsed_entities = collapse_spaced_entities.sub("&#\\2;", collapsed_spaces)

    return collapsed_entities.strip(" \n")


def orthofix(text, replacements):
    if len(replacements) > 0:
        last = 0
        line = []

        for j in regex.finditer(r"([^-'[:alpha:]](?:[^-[:alpha:]']*[^-'[:alpha:]])?)", text):
            if last != j.start():
                line.append((text[last:j.start()], "w"))
            line.append((text[j.start():j.end()], "s"))
            last = j.end()
        else:
            if last != len(text):
                line.append((text[last:], "w"))
        fixed_text = ""
        for j in line:
            if j[1] == "w":
                if j[0] in replacements:
                    fixed_text += replacements[j[0]]
                else:
                    fixed_text += j[0]
            else:
                fixed_text += j[0]
    else:
        fixed_text = text

    return fixed_text
