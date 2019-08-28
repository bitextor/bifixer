# bifixer
Tool to fix bitexts and tag near-duplicates for removal.

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

## What can BIFIXER do to your parallel corpora ##
* Fixes several text issues:
  * Fixes mojibake
  * Turns HTML entities into the character they represent 
  * Replaces characters from wrong alphabets with the correct ones
  * Deactivate this feature with `--ignore_characters`  
* Fixes common orthographic errors for some languages:
  * Currently: Danish, German, English, Spanish, Dutch, Norwegian, Portuguese and Turkish
  * Deactivate this feature with `--ignore_orthography`
* Removes sentences with empty source or target (deactivate this feature with `--ignore_empty`)
* Obtains hahes of parallel sentences, in order to ease the later removal of duplicates (deactivate this feature with `--ignore_duplicates`)
  * Want stronger deduplication? Make this feature to find near-duplicated sentences (ignoring casing, accents, diacritics and digits) by using the  `--aggressive_dedup` flag
  * Learn more in the "Tagging duplicated and near-duplicated sentences" section below.
* Provides better segmentation of long sentences:
  * Choose between [NLTK](https://www.nltk.org/)  or [Loomchild](https://github.com/mbanon/segment) (SRX-rules based) segmenter modules with `--segmenter`  (default is NLTK)
  * Choose the minimum length (in words) you want to start segmenting at (default is 15) with `--words_before_segmenting`. Set it to 1 to try to segment all sentences.
  * Deactivate this feature with `--ignore_segmentation`

 
## INSTALLATION ##
 
 ```bash
 python3.6 -m pip install -r bifixer/requirements.txt
```
Automatic testing was added to ensure that everything is working fine in Bifixer:

```bash
cd bifixer/tests
pytest
```
### Loomchild segmenter ###

Please note that, in order to use the optional `loomchild` segmenter module in Java, it has to be installed separatelly. Please follow [this](https://github.com/mbanon/segment#installation) extra instructions:

```bash
git submodule foreach git pull
cd segment/segment
mvn clean install
cd ../segment-ui
mvn clean install
cd target
unzip segment-2.0.2-SNAPSHOT.zip
```

In case you are not using Java 8 as default, download it and overwrite the 'JAVA_HOME' variable before installing, for example:

```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
```

## USAGE ##

### Bifixer ###

```
usage: bifixer.py [-h] [--scol SCOL] [--tcol TCOL] 
                  [--ignore_characters]
                  [--ignore_empty] 
                  [--ignore_orthography]
                  [--ignore_duplicates] [--aggressive_dedup]
                  [--ignore_segmentation] [--words_before_segmenting WORDS_BEFORE_SEGMENTING] [--segmenter {nltk,loomchild}]
                  [--tmp_dir TMP_DIR] 
                  [-q]
                  [--debug] [--logfile LOGFILE]
                  [-v]
                  input output srclang trglang


positional arguments:
  input                 Tab-separated files to be bifixed
  output                Fixed corpus
  srclang               Source language (SL) of the input
  trglang               Target language (TL) of the input

optional arguments:
  -h, --help            show this help message and exit

Optional:
  --scol SCOL           Source sentence column (starting in 1) (default: 3)
  --tcol TCOL           Target sentence column (starting in 1) (default: 4)
  --ignore_characters   Doesn't fix mojibake, orthography, or other character
                        issues (default: False)
  --ignore_empty        Doesn't remove sentences with empty source or target
                        (default: False)
  --ignore_orthography  Doesn't apply orthography fixing (default: False)
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
  --tmp_dir TMP_DIR     Temporary directory where creating the temporary files
                        of this program (default: /tmp)

Logging:
  -q, --quiet           Silent logging mode (default: False)
  --debug               Debug logging mode (default: False)
  --logfile LOGFILE     Store log to a file (default: <_io.TextIOWrapper
                        name='<stderr>' mode='w' encoding='UTF-8'>)
  -v, --version         show version of this script and exit

```

### Parameters ###

* Positional:
    * INPUT : Input file. Tab-separated bilingual input file. By default, the expected columns are: SRC_URL TRG_URL SRC_SENTENCE TRG_SENTENCE [EXTRA COLUMNS]
    * OUTPUT : Output file. Tab-separated bilingual output file, being a fixed version of the input file. By default, the output columns are: SRC_URL TRG_URL SRC_SENTENCE TRG_SENTENCE [EXTRA COLUMNS] HASH RANKING
    * SRC LANG : Source language code (2-letter ISO 639-1 code)
    * TRG LANG : Target language code (2-letter ISO 639-1 code)
* Optional:
    * --tmp_dir TMP_DIR : Directory for temporary files
    * --scol SCOL : Position of the source sentence column (starting in 1). Default: 3
    * --tcol TCOL : Position of the target sentence column (starting in 1). Default: 4
    * --ignore_duplicates : Deactivates deduplication (won't add hash or ranking)
    * --ignore_empty : Doesn't remove sentences with empty source or target
    * --ignore_segmentation : Deactivates segmentation of long sentences
    * --segmenter: Segmenter module (`nltk` or `loomchild`)
    * --words_before_segmenting : Maximum allowed amount of words in a sentence, before trying to segment it. Default: 15
    * --ignore_characters : Deactivates text fixing (characters, encoding...)
    * --ignore_orthography  Deactivates orthography fixing
    * --aggressive_dedup : Treats near-duplicated sentences as duplicates (normalizes sentences before hashing)
    * --tmp_dir TMP_DIR : Directory for temporary files
    * -q, --quiet : Silent logging mode
    * --debug: Shows debug messages while running
    * --logfile LOGFILE : Stores log into a file
    * -v, --version : Shows version number and exits
    * -h, --help: Shows help and exits
    
## RUN ##

### Single thread run ###

```bash
python3.6 bifixer/bifixer.py input-corpus.en-es output-corpus.en-es en es 
```

### Running in parallel ###

`bifixer.py` can be parallelized by using your favourite method (for example, GNU parallel)

Suggested usage: 

```bash
cat input-corpus.en-es | parallel -j 25 --pipe -k -l 30000 parallel-bf.sh en es > output-corpus.en-es 
```

with `parallel-bf.sh` being:

```bash
#!/bin/bash


INPUT_FILE=$(mktemp)

cat > $INPUT_FILE

python3.6 bifixer.py ${INPUT_FILE} ${INPUT_FILE}.o $1 $2 $3 &>bf.log

cat ${INPUT_FILE}.o

rm -Rf $INPUT_FILE ${INPUT_FILE}.o
```

## TAGGING DUPLICATED AND NEAR-DUPLICATED SENTENCES ##

In order to ease the later removal of duplicated or near-duplicated parallel sentences, Bifixer appends each parallel sentence two new fields: `hash`and `ranking`.

The hash is obtained by using the [XXHash](http://www.xxhash.com) algorithm, applied after fixing source and target sentences  (`fixed_source+"\t"+fixed_target`). Sentences that are identical at this step (see example below) will get the same hash. 

When using the `--aggressive_dedup` feature, fixed parallel sentences are also normalized (ignoring casing, accents and diacritics) before their hash is computed. Doing so, sentences that are near-duplicates (i.e. they only differ in casing or accents) will also get the same hash. Normalization is only used internally: the output sentences will not be normalized after Bifixer is applied. 

A `ranking` column is added at the end of each line. When not using the `--aggressive_dedup` feature, the number is set to 1 by default. When using the `--aggressive_dedup` feature, a float number is provided. This number (interpreted as the higher the better) will be used at later step to help the deduplication algorithm to choose the best sentence from those sharing the same hash. If the ranking number is exactly the same for a group of sentences sharing the same hash, only a random one should be kept. Otherwise, the one with the highest ranking number should be kept. 

## EXAMPLE ##

Input file:

```
http://www.ehyz.com/2.html.tmp	http://www.ehyz.com/2.html.tmp	1 year ago NuVid	Hace 1 aÃ±o NuVid
http://pandafoundation.com/index.php?page=7	http://pandafoundation.com/index.php?page=26	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!     
http://www.boliviamall.com/4520.html	http://www.boliviamall.com/4520.html	Welcome Guest 1! Would you like to log in ?	Bienvenido Invitado 1! ¿Le gustaria entrar ?    
http://pandafoundation.com/index.php?page=157	http://pandafoundation.com/index.php?page=76	©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved	©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!
http://www.ehyz.com/6.html.tmp	http://www.ehyz.com/6.html.tmp	1 year ago NuVid	Hace 1 año NuVid
http://www.boliviamall.com/4305.html	http://www.boliviamall.com/4305.html	Welcome Guest 12! Would you like to log in?	¡Bienvenido invitado 12! ¿Le gustaria entrar? 
```

Output file (using the '--aggressive_dedup' feature, otherwise ranking number would be 1 in all cases):

```
 
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
