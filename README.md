# bifixer
Tool to fix bitexts and tag near-duplicates for removal.

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

## What can BIFIXER do to your parallel corpora ##

* Fixes several text issues:
  * Fixes mojibake
  * Turns HTML entities into the character they represent
  * Replaces characters from wrong alphabets with the correct ones
  * Deactivate this feature with `--ignore_characters` 
* Normalizes punctuation and spaces (deactivate this feature with `--ignore_normalization`)
* Removes HTML tags (deactivate this feature with `--ignore_html`)
* Fixes common orthographic errors for some languages:
  * Currently: Danish, German, English, Spanish, Dutch, Norwegian, Portuguese and Turkish
  * Deactivate this feature with `--ignore_orthography`
* Removes sentences with empty source or target (deactivate this feature with `--ignore_empty`)
* Fixes common tokenization issues (deactivate this feature with `--ignore_detokenization`)
* Obtains hahes of parallel sentences, in order to ease the later removal of duplicates (deactivate this feature with `--ignore_duplicates`)
  * Want stronger deduplication? Make this feature to find near-duplicated sentences (ignoring casing, accents, diacritics and digits) by using the  `--aggressive_dedup` flag
  * Learn more in the "Tagging duplicated and near-duplicated sentences" section below.
* Provides better segmentation of long sentences:
  * Choose between [NLTK](https://www.nltk.org/)  or [Loomchild](https://github.com/mbanon/segment) (SRX-rules based) segmenter modules with `--segmenter`  (default is NLTK)
  * Choose the minimum length (in words) you want to start segmenting at (default is 15) with `--words_before_segmenting`. Set it to 1 to try to segment all sentences.
  * Deactivate this feature with `--ignore_segmentation`
* Got MONOLINGUAL text? Use `monofixer.py` instead.

## Citation

If you find Bifixer useful, please consider citing the following paper:

> Gema Ramírez-Sánchez, Jaume Zaragoza-Bernabeu, Marta Bañón and Sergio Ortiz Rojas \
> "[Bifixer and Bicleaner: two open-source tools to clean your parallel data.](https://eamt2020.inesc-id.pt/proceedings-eamt2020.pdf#page=311)",\
>in *Proceedings of the 22nd Annual Conference of the European Association for Machine Translation*.\
>Lisboa, Portugal: European Association for Machine Translation, November 2020

```latex
@InProceedings{prompsit:2020:EAMT,
  author    = {Gema Ram\'{i}rez-S\'{a}nchez and Jaume Zaragoza-Bernabeu and Marta Ba{\~n}\'{o}n and Sergio Ortiz-Rojas},
  title     = {Bifixer and Bicleaner: two open-source tools to clean your parallel data.},
  booktitle = {Proceedings of the 22nd Annual Conference of the European Association for Machine Translation},
  pages	    = {291--298},
  isbn      = {978-989-33-0589-8},
  year	    = {2020},
  month     = {November},
  address   = {Lisboa, Portugal},
  publisher = {European Association for Machine Translation}
}
```

## INSTALLATION ##

Install from source:

```bash
git clone https://github.com/bitextor/bifixer
cd bifixer
pip install .
```

Automatic testing was added to ensure that everything is working fine in Bifixer:

```bash
cd bifixer
pytest
```

Or install without manually downloading the repo:

```bash
pip install "bifixer @ git+https://github.com/bitextor/bifixer.git"
```
Or even easier, install directly from PyPI:
```bash
pip install bifixer
```

Also, you can install the conda package:

```bash
conda install -c bitextor bifixer
```

After installing, two executables (`bifixer` and `monofixer`) will be available to be run.

### Loomchild segmenter ###

Please note that, in order to use the optional `loomchild` segmenter module in Java, it has to be specified as an optional dependency during installation:

```bash
pip install bifixer[loomchild]
```

In case you are not using Java 8 as default, download it and overwrite the 'JAVA_HOME' variable before installing, for example:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
```

## USAGE ##

### Bifixer ###

```bash
usage: bifixer.py [-h] [--header] [--scol SCOL] [--tcol TCOL]
                  [--sdeferredcol SDEFERREDCOL] [--tdeferredcol TDEFERREDCOL]
                  [--ignore_characters] [--ignore_empty] [--ignore_long]
                  [--ignore_orthography] [--ignore_detokenization]
                  [--ignore_duplicates] [--aggressive_dedup]
                  [--ignore_segmentation] [--ignore_html]
                  [--words_before_segmenting WORDS_BEFORE_SEGMENTING]
                  [--segmenter {nltk,loomchild}] [--annotated_output] [--tmp_dir TMP_DIR] [-q]
                  [--debug] [--logfile LOGFILE] [-v]
                  input output srclang trglang

positional arguments:
  input                 Tab-separated files to be bifixed
  output                Fixed corpus
  srclang               Source language (SL) of the input
  trglang               Target language (TL) of the input

optional arguments:
  -h, --help            show this help message and exit

Optional:
  --header              Input file will have header (default: False)
  --scol SCOL           Source sentence column (starting in 1). The name of
                        the field is expected instead of the position if
                        --header is set (default: 3)
  --tcol TCOL           Target sentence column (starting in 1). The name of
                        the field is expected instead of the position if
                        --header is set (default: 4)
  --sdeferredcol SDEFERREDCOL
                        Source deferred standoff annotation column (starting
                        in 1). The name of the field is expected instead of
                        the position if --header is set (default: None)
  --tdeferredcol TDEFERREDCOL
                        Target deferred standoff annotation column (starting
                        in 1). The name of the field is expected instead of
                        the position if --header is set (default: None)
  --ignore_characters   Doesn't fix mojibake, orthography, or other character
                        issues (default: False)
  --ignore_empty        Doesn't remove sentences with empty source or target
                        (default: False)
  --ignore_long         Doesn't ignore too long sentences (default: False)
  --ignore_orthography  Doesn't apply orthography fixing (default: False)
  --ignore_html		Doesn't remove HTML tags (default: False)
  --ignore_detokenization
                        Doesn't fix common tokenization issues (default:
                        False)
  --ignore_duplicates   Doesn't obtain the hashes of parallel sentences
                        (default: False)
  --aggressive_dedup    Treats similar sentences as duplicates (marking them
                        with the same hash) (default: False)
  --ignore_segmentation
                        Doesn't change segmentation of long sentences
                        (default: False)
  --words_before_segmenting WORDS_BEFORE_SEGMENTING
                        Max words allowed in one side of a parallel sentence
                        before trying to segmentate it. Set to 0 to applicate
                        segmentation on everything. (default: 15)
  --segmenter {nltk,loomchild}
                        Segmenter module. (default: nltk)
  --annotated_output    Adds an extra column indicating if the sentence pair was modified
			 ('Yes' if it was modified, otherwise 'No') (default: False)

  --tmp_dir TMP_DIR     Temporary directory where creating the temporary files
                        of this program (default: /tmp)

Logging:
  -q, --quiet           Silent logging mode (default: False)
  --debug               Debug logging mode (default: False)
  --logfile LOGFILE     Store log to a file (default: <_io.TextIOWrapper
                        name='<stderr>' mode='w' encoding='UTF-8'>)
  -v, --version         show version of this script and exit
```

#### Parameters ####

* Positional:
  * INPUT : Input file. Tab-separated bilingual input file. By default, the expected columns are: SRC_URL TRG_URL SRC_SENTENCE TRG_SENTENCE [EXTRA COLUMNS]. When INPUT is -, reads standard input.
  * OUTPUT : Output file. Tab-separated bilingual output file, being a fixed version of the input file. By default, the output columns are: SRC_URL TRG_URL SRC_SENTENCE TRG_SENTENCE [EXTRA COLUMNS] HASH RANKING. When OUTPUT is -, writes standard input.
  * SRC LANG : Source language code (2-letter ISO 639-1 code)
  * TRG LANG : Target language code (2-letter ISO 639-1 code)
* Optional:
  * --tmp_dir TMP_DIR : Directory for temporary files
  * --header : Treats the first sentence of the input file as the header row. If set, the output will contain a header as well
  * --scol SCOL : Position of the source sentence column (starting in 1). If `--header` is set, the expected value will be the name of the field. Default: 3 if `--header` is not set else src_text
  * --tcol TCOL : Position of the target sentence column (starting in 1). If `--header` is set, the expected value will be the name of the field. Default: 4 if `--header` is not set else trg_text
  * --sdeferredcol SDEFERREDCOL : Source deferred standoff annotation column (starting in 1). Default: None
  * --tdeferredcol TDEFERREDCOL : Target deferred standoff annotation column (starting in 1). Default: None
  * --ignore_duplicates : Deactivates deduplication (won't add hash or ranking)
  * --ignore_empty : Doesn't remove sentences with empty source or target
  * --ignore_long: Doesn't remove too long sentences
  * --ignore_html: Doesn't remove HTML tags
  * --ignore_segmentation : Deactivates segmentation of long sentences
  * --segmenter: Segmenter module (`nltk` or `loomchild`). Default: nltk
  * --words_before_segmenting : Maximum allowed amount of words in a sentence, before trying to segment it. Default: 15
  * --ignore_characters : Deactivates text fixing (characters, encoding...)
  * --ignore_orthography  Deactivates orthography fixing
  * --ignore_detokenization : Doesn't fix common tokenization issues.
  * --aggressive_dedup : Treats near-duplicated sentences as duplicates (normalizes sentences before hashing)
  *  --annotated_output    Adds an extra column indicating if the sentence pair was modified ('Yes' if it was modified, otherwise 'No'). Default: False
  * --tmp_dir TMP_DIR : Directory for temporary files
  * -q, --quiet : Silent logging mode
  * --debug: Shows debug messages while running
  * --logfile LOGFILE : Stores log into a file
  * -v, --version : Shows version number and exits
  * -h, --help: Shows help and exits


### Monofixer ###

```bash
python3.7 bifixer/monofixer.py --help
usage: monofixer.py [-h] 
                    [--scol SCOL] [--sdeferredcol SDEFERREDCOL]
                    [--ignore_characters] [--ignore_long]
                    [--ignore_orthography] [--ignore_detokenization]
                    [--ignore_duplicates] [--aggressive_dedup]
                    [--ignore_segmentation] [--ignore_html]
                    [--words_before_segmenting WORDS_BEFORE_SEGMENTING]
                    [--segmenter {nltk,loomchild}] [--annotated_output] [--tmp_dir TMP_DIR] [-q]
                    [--debug] [--logfile LOGFILE] [-v]
                    input output lang

positional arguments:
  input                 Tab-separated file to be fixed
  output                Fixed corpus
  lang                  Language of the input

optional arguments:
  -h, --help            show this help message and exit

Optional:
  --header              Input file will have header (default: False)
  --scol SCOL           Sentence column (starting in 1). The name of the
                        field is expected instead of the position if --header
                        is set (default: 2)
  --sdeferredcol SDEFERREDCOL
                        Source deferred standoff annotation column (starting
                        in 1). The name of the field is expected instead of
                        the position if --header is set (default: None)
  --ignore_characters   Doesn't fix mojibake, orthography, or other character
                        issues (default: False)
  --ignore_long         Doesn't ignore too long sentences (default: False)
  --ignore_orthography  Doesn't apply orthography fixing (default: False)
  --ignore_detokenization
                        Doesn't fix common tokenization issues (default:
                        False)
  --ignore_html		Doesn't remove HTML tags (default: False)
  --ignore_duplicates   Doesn't obtain the hashes of sentences (default:
                        False)
  --aggressive_dedup    Treats similar sentences as duplicates (marking them
                        with the same hash) (default: False)
  --ignore_segmentation 
                        Doesn't change segmentation of long sentences
                        (default: False)
  --words_before_segmenting WORDS_BEFORE_SEGMENTING
                        Max words allowed in a parallel sentence before trying
                        to segmentate it. Set to 0 to applicate segmentation
                        on everyt33hing. (default: 15)
  --segmenter {nltk,loomchild}
                        Segmenter module. (default: nltk)
  --annotated_output    Adds an extra column indicating if the sentence  was
			 modified ('Yes' if it was modified, otherwise 'No')
			 (default: False)
  --tmp_dir TMP_DIR     Temporary directory where creating the temporary files
                        of this program (default: /tmp)

Logging:
  -q, --quiet           Silent logging mode (default: False)
  --debug               Debug logging mode (default: False)
  --logfile LOGFILE     Store log to a file (default: <_io.TextIOWrapper
                        name='<stderr>' mode='w' encoding='UTF-8'>)
  -v, --version         show version of this script and exit
```

#### Parameters ####

* Positional:
  * INPUT : Input file. Tab-separated monolingual input file. By default, the expected columns are: URL SENTENCE [EXTRA COLUMNS]. When INPUT is -, reads standard input.
  * OUTPUT : Output file. Tab-separated monolingual output file, being a fixed version of the input file. By default, the output columns are: URL SENTENCE [EXTRA COLUMNS] HASH RANKING. When OUTPUT is -, writes standard input.
  * LANG : Sentence language code (2-letter ISO 639-1 code)
* Optional:
  * --tmp_dir TMP_DIR : Directory for temporary files
  * --header : Treats the first sentence of the input file as the header row. If set, the output will contain a header as well
  * --scol SCOL : Position of the source sentence column (starting in 1). If `--header` is set, the expected value will be the name of the field. Default: 2 if `--header` is not set else src_text
  * --sdeferredcol SDEFERREDCOL  Sentence deferred standoff annotation column (starting in 1). Default: None
  * --ignore_duplicates : Deactivates deduplication (won't add hash or ranking)
  * --ignore_long: Doesn't remove too long sentences
  * --ignore_html: Doesn't remove HTML tags
  * --ignore_segmentation : Deactivates segmentation of long sentences
  * --segmenter: Segmenter module (`nltk` or `loomchild`). Default: nltk
  * --words_before_segmenting : Maximum allowed amount of words in a sentence, before trying to segment it. Default: 15
  * --ignore_characters : Deactivates text fixing (characters, encoding...)
  * --ignore_orthography : Deactivates orthography fixing
  * --ignore_detokenization : Doesn't fix common tokenization issues.
  * --aggressive_dedup : Treats near-duplicated sentences as duplicates (normalizes sentences before hashing)
  * --annotated_output    Adds an extra column indicating if the sentence was modified ('Yes' if it was modified, otherwise 'No'). Default: False
  * --tmp_dir TMP_DIR : Directory for temporary files
  * -q, --quiet : Silent logging mode
  * --debug: Shows debug messages while running
  * --logfile LOGFILE : Stores log into a file
  * -v, --version : Shows version number and exits
  * -h, --help: Shows help and exits


## RUN ##

### Single thread run ###

```bash
bifixer input-corpus.en-es output-corpus.en-es en es 
```

### Running in parallel ###

`bifixer` can be parallelized by using your favourite method (for example, GNU parallel)

Suggested usage:

```bash
cat input-corpus.en-es \
    | parallel -j 25 --pipe -k -l 30000 bifixer -q - - en es \
    > output-corpus.en-es 
```

where the two '`-`' mean read from stdin and write to stdout, and the `-q` tells bifixer to be quiet in order to avoid logging a lot of information messages.

## TAGGING DUPLICATED AND NEAR-DUPLICATED SENTENCES ##

In order to ease the later removal of duplicated or near-duplicated parallel sentences, Bifixer appends each parallel sentence two new fields: `hash`and `ranking`.

The hash is obtained by using the [XXHash](http://www.xxhash.com) algorithm, applied after fixing source and target sentences  (`fixed_source+"\t"+fixed_target`). Sentences that are identical at this step (see example below) will get the same hash.

When using the `--aggressive_dedup` feature, fixed parallel sentences are also normalized (ignoring casing, accents and diacritics) before their hash is computed. Doing so, sentences that are near-duplicates (i.e. they only differ in casing or accents) will also get the same hash. Normalization is only used internally: the output sentences will not be normalized after Bifixer is applied.

A `ranking` column is added at the end of each line. When not using the `--aggressive_dedup` feature, the number is set to 1 by default. When using the `--aggressive_dedup` feature, a float number is provided. This number (interpreted as the higher the better) will be used at later step to help the deduplication algorithm to choose the best sentence from those sharing the same hash. If the ranking number is exactly the same for a group of sentences sharing the same hash, only a random one should be kept. Otherwise, the one with the highest ranking number should be kept.

## EXAMPLE ##

Input file:

```text
http://www.ehyz.com/2.html.tmp	http://www.ehyz.com/2.html.tmp	1 year ago NuVid	Hace 1 aÃ±o NuVid
http://pandafoundation.com/index.php?page=7	http://pandafoundation.com/index.php?page=26	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!     
http://www.boliviamall.com/4520.html	http://www.boliviamall.com/4520.html	Welcome Guest 1! Would you like to log in ?	Bienvenido Invitado 1! ¿Le gustaria entrar ?    
http://pandafoundation.com/index.php?page=157	http://pandafoundation.com/index.php?page=76	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!
http://www.ehyz.com/6.html.tmp	http://www.ehyz.com/6.html.tmp	1 year ago NuVid	Hace 1 año NuVid
http://www.boliviamall.com/4305.html	http://www.boliviamall.com/4305.html	Welcome Guest 12! Would you like to log in?	¡Bienvenido invitado 12! ¿Le gustaria entrar? 
```

Output file (using the '--aggressive_dedup' feature, otherwise ranking number would be 1 in all cases):

```text
 
http://www.ehyz.com/2.html.tmp	http://www.ehyz.com/2.html.tmp	1 year ago NuVid	Hace 1 año NuVid	9f1f7c6fc775a23a	88.25
http://pandafoundation.com/index.php?page=7	http://pandafoundation.com/index.php?page=26	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!	d0278d1279f06823	91.93
http://www.boliviamall.com/4520.html	http://www.boliviamall.com/4520.html	Welcome Guest 1! Would you like to log in ?	Bienvenido Invitado 1! ¿Le gustaría entrar ?	e8f129b1624b9f5d	91.22
http://pandafoundation.com/index.php?page=157	http://pandafoundation.com/index.php?page=76	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!	d0278d1279f06823	91.93
http://www.ehyz.com/6.html.tmp	http://www.ehyz.com/6.html.tmp	1 year ago NuVid	Hace 1 año NuVid	9f1f7c6fc775a23a	88.25
http://www.boliviamall.com/4305.html	http://www.boliviamall.com/4305.html	Welcome Guest 12! Would you like to log in?	¡Bienvenido invitado 12! ¿Le gustaría entrar?	422aeefd8f056b30	92.78
```

___

![Connecting Europe Facility](https://www.paracrawl.eu/images/logo_en_cef273x39.png)

All documents and software contained in this repository reflect only the authors' view. The Innovation and Networks Executive Agency of the European Union is not responsible for any use that may be made of the information it contains.
