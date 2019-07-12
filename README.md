# bifixer
Massively scalable, frugal corpora fixer &amp; deduper.

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

## What can BIFIXER  do ##
* Fixes several text issues:
  * Fixes mojibake
  * Turns HTML entities into the character they represent 
  * Replaces characters from wrong alphabets with the correct ones
  * Fixes common orthographic errors for some languages (currently, only English)
  * Deactivate this feature with `--ignore_characters`
* Removes sentences with empty source or target (deactivate this feature with `--ignore_empty`)
* Removes duplicated parallel sentences (deactivate this feature with `--ignore_duplicates`)
  * URLs are stored in an extra file (deactivate this feature with `--ignore_urls`)
  * Want stronger deduplication? Make this feature to remove similar sentences (ignoring casing, accents and diacritics) by using the  `--aggressive_dedup` flag
  * Learn more about this feature in the "Deduplication" section below
* COMING SOON: Provides better segmentation of long sentences (deactivate this feature with `--ignore_segmentation`)


### IMPORTANT WARNING ###

Since the setup and teardown are very destructive (it will remove ANY key in the selected DB), the parameter `--redis_db` is always mandatory.  This parameter (an integer from 0 to 15) makes Redis to internally segment the data into different DBs that work independently.
 
If you are running more than one Bifixer at the same time, each instance of Bifixer must be called with a different DB index. 
You can also configure the Redis host and port with parameters `--redis_host`, `--redis_port` and `--redis_password`  (by default, Redis will use `localhost:6379` )

 **PLEASE MAKE SURE THAT THE SELECTED DB IS NOT IN USE BY ANY OTHER APPLICATION**
 
 **PLEASE MAKE SURE THAT THE SELECTED DB IS NOT IN USE BY ANY OTHER RUNNING INSTANCE OF BIFIXER**
 
If you are not sure which DBs are in use in Redis, you can connect with Redis by using  `redis-cli -h HOST -p PORT`. Once connected, use the command `info` to get the DBs in use  (under the title `#Keyspace`).

 
## INSTALLATION ##
 
 ```bash
 sudo apt-get install redis-server redis-tools
 python3.6 -m pip install -r bifixer/requirements.txt
```

## USAGE ##

In order to ease running Bifixer in parallel, it's splitted into 3 different scripts:

* bifixer_setup.py : Starts and purges redis
* bifixer_lite.py : Fixes the corpus and does the dedup
* bifixer_teardown.py : Retrieves the data from redis and writes the URLs file, and then purges redis  (Optional)

A more detailed description and usage for each script is provided in the next section.

`bifixer_lite.py` can be parallelized by using your favourite method (for example, GNU parallel), while `bifixer_setup.py` and `bifixer_teardown.py` must be run only once (the setup before bifixer_lite, and the teardwon after bifixer_lite). See below for examples.

### Single thread run ###

```bash
python3.6 bifixer/bifixer_setup.py  --redis_db=0 \ 
&& python3.6 bifixer/bifixer_lite.py input-corpus.en-es output-corpus.en-es en es  --redis_db=0 \ 
&& python3.6 bifixer/bifixer_teardown.py  urlsfile.en-es --redis_db=0 
```

### Running in parallel ###

Suggested usage: 

```bash
python3.6 bifixer/bifixer_setup.py  --redis_db=0 && \
cat input-corpus.en-es | parallel -j 25 --pipe -k -l 30000 parallel-bf.sh en es --redis_db=0 > output-corpus.en-es && \ 
python3.6 bifixer/bifixer_teardown.py  urlsfile.en-es --redis_db=0 
```

with `parallel-bf.sh` being:

```bash
#!/bin/bash


INPUT_FILE=$(mktemp)

cat > $INPUT_FILE

python3.6 bifixer_lite.py ${INPUT_FILE} ${INPUT_FILE}.o $1 $2 $3 &>bf.log

cat ${INPUT_FILE}.o

rm -Rf $INPUT_FILE ${INPUT_FILE}.o
```

You can use your favourite parallelization method for `bifixer_lite.py`, but `bifixier_setup.py` and `bifixer_teardown.py` must NOT be parallelized.


## Bifixer setup ##

Starts a connection with Redis in the host,port and db indicated (or localhost:6379 if no host and port were explicited),
and then **removes everything in that host:port[db]**


```bash
usage: bifixer_setup.py [-h] --redis_db REDIS_DB [--redis_host REDIS_HOST]
                        [--redis_port REDIS_PORT]
                        [--redis_password REDIS_PASSWORD] [-q] [--debug]
                        [--logfile LOGFILE] [-v]

optional arguments:
  -h, --help            show this help message and exit

Mandatory:
  --redis_db REDIS_DB   Redis database index (default: None)

Optional:
  --redis_host REDIS_HOST
                        Redis host (default: localhost)
  --redis_port REDIS_PORT
                        Redis port (default: 6379)
  --redis_password REDIS_PASSWORD
                        Redis password (default: )

Logging:
  -q, --quiet           Silent logging mode (default: False)
  --debug               Debug logging mode (default: False)
  --logfile LOGFILE     Store log to a file (default: <_io.TextIOWrapper
                        name='<stderr>' mode='w' encoding='UTF-8'>)
  -v, --version         show version of this script and exit
```

### Parameters ###

* Mandatory:
    * --redis_db REDIS_DB : Index (0-15) of the Redis DB that will be used in this run of Bifixer. Any existing content WILL BE REMOVED.
* Optional:
    * --redis_host REDIS_HOST : Host machine of the Redis Server. Default: localhost
    * --redis_port REDIS_PORT : Port of the Redis Server. Default: 6379
    * --redis_password REDIS_PASSWORD: Password of the Redis Server. 
    * -q, --quiet : Silent logging mode
    * --debug: Shows debug messages while running
    * --logfile LOGFILE : Stores log into a file
    * -v, --version : Shows version number and exits
    * -h, --help: Shows help and exits


## Bifixer lite ##

Main core of Bifixer.
It fixes issues with characters and encoding, improves segmentation of long sentences, and removes duplicated sentences from the corpus.
All these features are optional.

```bash
usage: bifixer_lite.py [-h] [--scol SCOL] [--tcol TCOL] [--sucol SUCOL]
                       [--tucol TUCOL] --redis_db REDIS_DB [--tmp_dir TMP_DIR]
                       [--ignore_duplicates] [--ignore_empty]
                       [--ignore_segmentation] [--ignore_urls]
                       [--redis_host REDIS_HOST] [--redis_port REDIS_PORT]
                       [--redis_password REDIS_PASSWORD] [--urls URLS] [-q]
                       [--debug] [--logfile LOGFILE] [-v]
                       input output srclang trglang

positional arguments:
  input                 Tab-separated files to be bifixed
  output                Fixed corpus
  srclang               Source language (SL) of the input
  trglang               Target language (TL) of the input

optional arguments:
  -h, --help            show this help message and exit
Mandatory:
  --redis_db REDIS_DB   Redis database index (default: None)

Optional:
  --scol SCOL           Source sentence column (starting in 1) (default: 3)
  --tcol TCOL           Target sentence column (starting in 1) (default: 4)
  --sucol SUCOL         Source URL column (starting in 1) (default: 1)
  --tucol TUCOL         Target URL column (starting in 1) (default: 2)
  --ignore_characters   Doesn't fix mojibake, orthography, or other character
                        issues (default: False)
  --ignore_duplicates   Doesn't remove duplicated parallel sentences (default:
                        False)
  --ignore_empty        Doesn't remove sentences with empty source or target
                        (default: False)
  --ignore_urls         Doesn't save an URLs file when deduplicating (default:
                        False)
  --aggressive_dedup    Treats similar sentences as duplicates (removing them)
                        (default: False)
  --redis_host REDIS_HOST
                        Redis host (default: localhost)
  --redis_port REDIS_PORT
                        Redis port (default: 6379)
  --redis_password REDIS_PASSWORD
                        Redis password (default: )
  --ignore_segmentation
                        Doesn't change segmentation of long sentences
                        (default: False)
  --words_before_segmenting WORDS_BEFORE_SEGMENTING
                        Max words allowed in one side of a parallel sentence
                        before trying to segmentate it. Set to 0 to applicate
                        segmentation on everything. (default: 40)
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
    * OUTPUT : Output file. Tab-separated bilingual output file, being a fixed version of the input file. By default, the output columns are: SRC_SENTENCE TRG_SENTENCE [EXTRA COLUMNS] HASH
    * SRC LANG : Source language code (2-letter ISO 639-1 code)
    * TRG LANG : Target language code (2-letter ISO 639-1 code)
* Mandatory:
    * --redis_db REDIS_DB : Index (0-15) of the Redis DB that will be used in this run of Bifixer. Any existing content WILL BE REMOVED.
* Optional:
    * --redis_host REDIS_HOST : Host machine of the Redis Server. Default: localhost
    * --redis_port REDIS_PORT : Port of the Redis Server. Default: 6379
    * --redis_password REDIS_PASSWORD: Password of the Redis Server. 
    * --tmp_dir TMP_DIR : Directory for temporary files
    * --scol SCOL : Position of the source sentence column (starting in 1). Default: 3
    * --tcol TCOL : Position of the target sentence column (starting in 1). Default: 4
    * --sucol SUCOL : Position of the source URL column (starting in 1). Default: 1
    * --tucol TUCOL : Position of the target URL column (starting in 1). Default: 2
    * --ignore_duplicates : Deactivates deduplication (won't remove duplicated sentences)
    * --ignore_empty : Doesn't remove sentences with empty source or target
    * --ignore_segmentation : Deactivates segmentation of long sentences
    * --words_before_segmenting : Maximum allowed amount of words in a sentence, before trying to segment it. Default: 40
    * --ignore_characters : Deactivates text fixing
    * --ignore_urls: Deactivates the URL saving feature for deduplicated sentences
    * --aggressive_dedup : Treats similar sentences as duplicates
    * --tmp_dir TMP_DIR : Directory for temporary files
    * -q, --quiet : Silent logging mode
    * --debug: Shows debug messages while running
    * --logfile LOGFILE : Stores log into a file
    * -v, --version : Shows version number and exits
    * -h, --help: Shows help and exits
    

## Bifixer teardown ##

This script gets all the hashes and URLs stored in Redis by `bifixer_lite.py`, and writes them in a text file.
At the end,  **removes everything in that host:port[db]**
If you are not interested in retrieving the URLs of removed duplicated sentences, you don't need to run this script.

```bash
usage: bifixer_teardown.py [-h] --redis_db REDIS_DB [--tmp_dir TMP_DIR]
                           [--redis_host REDIS_HOST] [--redis_port REDIS_PORT]
                           [--redis_password REDIS_PASSWORD] [-q] [--debug]
                           [--logfile LOGFILE] [-v]
                           urls

positional arguments:
  urls                  Output URLs file

optional arguments:
  -h, --help            show this help message and exit

Mandatory:
  --redis_db REDIS_DB   Redis database index (default: None)

Optional:
  --tmp_dir TMP_DIR     Temporary directory where creating the temporary files
                        of this program (default: /tmp)
  --redis_host REDIS_HOST
                        Redis host (default: localhost)
  --redis_port REDIS_PORT
                        Redis port (default: 6379)
  --redis_password REDIS_PASSWORD
                        Redis password (default: )

Logging:
  -q, --quiet           Silent logging mode (default: False)
  --debug               Debug logging mode (default: False)
  --logfile LOGFILE     Store log to a file (default: <_io.TextIOWrapper
                        name='<stderr>' mode='w' encoding='UTF-8'>)
  -v, --version         show version of this script and exit
```

### Parameters ###

* Positional:
    * URLS : Output URLs file (will be overwritten if exists). See section "Deduplication" for this file's format.
* Mandatory:
    * --redis_db REDIS_DB : Index (0-15) of the Redis DB that will be used in this run of Bifixer. Any existing content WILL BE REMOVED.
* Optional:
    * --redis_host REDIS_HOST : Host machine of the Redis Server. Default: localhost
    * --redis_port REDIS_PORT : Port of the Redis Server. Default: 6379
    * --redis_password REDIS_PASSWORD: Password of the Redis Server. 
    * --tmp_dir TMP_DIR : Directory for temporary files
    * -q, --quiet : Silent logging mode
    * --debug: Shows debug messages while running
    * --logfile LOGFILE : Stores log into a file
    * -v, --version : Shows version number and exits
    * -h, --help: Shows help and exits
    

## DEDUPLICATION ##

Deduplication is achieved by extracting the hash of each pair of parallel sentences (or a normalized version of the parallel sentence, if the flag `--aggressive_dedup` is set). 

In order to not lose information such as source and target URLs for the removed sentences, we store them in a Redis database, using the hash as key. 

At the end of the process, two files are produced: the output file (containing deduplicated sentences, without URLs columns, and with an extra Hash column) and the urls file (containing hashes, and the associated urls for each hash). Thus, each parallel sentence can be reconstructed with all the URLs where it was found.

## EXAMPLE ##

Input file:

```
http://www.ehyz.com/59/en/326/tease/long/2.html.tmp     http://www.ehyz.com/ca/es/326/tease/long/2.html.tmp     1 year ago NuVid        Hace 1 aÃ±o NuVid       8.03571 -15.407790323142798     0.641647501152572
https://www.kosmos.com.mx/tienda/catalog/accessories-c-215_216_275_494.html?language=en https://www.kosmos.com.mx/tienda/catalog/accesorios-c-215_216_275_494.html?sort=5a      1xStarSeek Telescope Control Cable      1xCable StarSeek para Control de Telescope     1.44375 -56.48520975306523      0.5047093235143448
http://www.bluelakesports.com/index.php?cPath=227_245&sort=2a&language=de       http://www.bluelakesports.com/product_reviews.php?products_id=1280      1x Weber Baby Ledermokassins    2x Weber mocasines de cuero del beb     0.853846      -79.7304142689   0.5513269485697172
http://www.goldnatura.com/price_match.php?products_id=509       http://www.goldnatura.com/animal-nitro-packs-p-193.html?language=es     1x XTRACT 80 caps.      1x XTRACT 80 capsulas   8.04375 -49.6418307716  0.6567062692359137
http://www.ehyz.com/a6/en/782/glasses/long/6.html.tmp   http://www.ehyz.com/ed/es/782/glasses/long/6.html.tmp   1 year ago NuVid        Hace 1 aÃ±o NuVid       8.03571 -15.407790323142798     0.641647501152572
http://pandafoundation.com/e/ensearch/index.php?page=7&keyboard=&startdate=2014-01-01&enddate=2014-01-31        http://pandafoundation.com/e/essearch/index.php?page=26&keyboard=&startdate=2017-06-01&enddate=2017-06-30       ©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved      ©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!     1.64062 -11.542366408213208     0.5882183928033842
http://www.boliviamall.com/en/art/san-francisco-de-potosi-painting-p-4520.html  http://www.boliviamall.com/es/arte/cuadro-san-francisco-de-potosi-p-4520.html   Welcome Guest ! Would you like to log in ?      Bienvenido Invitado! ¿Le gustaria entrar ?     0.27    -0.08376375463397157    0.6631008397989712
https://www.somatex.com/en/mamma-interventions/wire-marking/duo-system.html?___from_store=en    https://www.somatex.com/es/intervenciones-de-mama/marcaje-con-alambre/duo-system.html?___from_store=es  Needle Guides Sets - latex      Kit de guías de aguja – incluye látex  0.643478        -30.106423314714927     0.5633602240130181
http://rosarioturismo.com/en/gallery/galeriafotos.php?c=&s=&f=1210&pagina=13    http://rosarioturismo.com/es/galeria/galeriafotos.php?c=&s=&f=1261&pagina=13    Parks and Walks Green Space Trails Go to        Parques y paseos Recorridos entre espacios verdes Entrar       0.492157        -22.1581658352  0.6005954269112532
http://pandafoundation.com/e/ensearch/index.php?page=157&keyboard=&startdate=2014-08-01&enddate=2014-08-31      http://pandafoundation.com/e/essearch/index.php?page=76&keyboard=&startdate=2018-02-01&enddate=2018-02-28       ©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved      ©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!     1.64062 -11.542366408213208     0.5882183928033841
```

Output file:

```
1 year ago NuVid        Hace 1 año NuVid        8.03571 -15.407790323142798     0.641647501152572       14d8115c65f1948891f6b77402a43cb2
1xStarSeek Telescope Control Cable      1xCable StarSeek para Control de Telescope      1.44375 -56.48520975306523      0.5047093235143448      e4a1478e3c1c017945dc8796e8fa8db1
1x Weber Baby Ledermokassins    2x Weber mocasines de cuero del beb     0.853846        -79.7304142689  0.5513269485697172      72fea54269f075259d9a063e5a32bcef
1x XTRACT 80 caps.      1x XTRACT 80 capsulas   8.04375 -49.6418307716  0.6567062692359137      cfea88e289c9fe00dd7d9398e1423292
©2007 Chengdu Research Base of Giant Panda Breeding ! All Rights Reserved       ©2017 Fundación para la Investigación de Cría del Panda Gigante de Chengdu/ ¡Todos los derechos reservados!     1.64062 -11.542366408213208     0.5882183928033842     1ab206ab29fd0b002851d5c8e926c5bd
Welcome Guest ! Would you like to log in ?      Bienvenido Invitado! ¿Le gustaria entrar ?      0.27    -0.08376375463397157    0.6631008397989712      8dac8335e37a3b6d1eb41f882b15b799
Needle Guides Sets - latex      Kit de guías de aguja – incluye látex   0.643478        -30.106423314714927     0.5633602240130181      182813ac6ba5df670e7f3d04c431ad46
Parks and Walks Green Space Trails Go to        Parques y paseos Recorridos entre espacios verdes Entrar        0.492157        -22.1581658352  0.6005954269112532      05f61c72acbc724d49571c3e09aed5f8
```

Note that two sentences were removed because they were duplicates (those starting with "©2007" and "1 year ago"). Also, the encoding of "aÃ±o" was corrected to "año".

URLs file:

```
cfea88e289c9fe00dd7d9398e1423292        ['http://www.goldnatura.com/price_match.php?products_id=509', 'http://www.goldnatura.com/animal-nitro-packs-p-193.html?language=es']
05f61c72acbc724d49571c3e09aed5f8        ['http://rosarioturismo.com/en/gallery/galeriafotos.php?c=&s=&f=1210&pagina=13', 'http://rosarioturismo.com/es/galeria/galeriafotos.php?c=&s=&f=1261&pagina=13']
182813ac6ba5df670e7f3d04c431ad46        ['https://www.somatex.com/en/mamma-interventions/wire-marking/duo-system.html?___from_store=en', 'https://www.somatex.com/es/intervenciones-de-mama/marcaje-con-alambre/duo-system.html?___from_store=es']
8dac8335e37a3b6d1eb41f882b15b799        ['http://www.boliviamall.com/en/art/san-francisco-de-potosi-painting-p-4520.html', 'http://www.boliviamall.com/es/arte/cuadro-san-francisco-de-potosi-p-4520.html']
72fea54269f075259d9a063e5a32bcef        ['http://www.bluelakesports.com/index.php?cPath=227_245&sort=2a&language=de', 'http://www.bluelakesports.com/product_reviews.php?products_id=1280']
1ab206ab29fd0b002851d5c8e926c5bd        ['http://pandafoundation.com/e/ensearch/index.php?page=7&keyboard=&startdate=2014-01-01&enddate=2014-01-31', 'http://pandafoundation.com/e/essearch/index.php?page=26&keyboard=&startdate=2017-06-01&enddate=2017-06-30', 'http://pandafoundation.com/e/ensearch/index.php?page=157&keyboard=&startdate=2014-08-01&enddate=2014-08-31', 'http://pandafoundation.com/e/essearch/index.php?page=76&keyboard=&startdate=2018-02-01&enddate=2018-02-28']
14d8115c65f1948891f6b77402a43cb2        ['http://www.ehyz.com/59/en/326/tease/long/2.html.tmp', 'http://www.ehyz.com/ca/es/326/tease/long/2.html.tmp', 'http://www.ehyz.com/a6/en/782/glasses/long/6.html.tmp', 'http://www.ehyz.com/ed/es/782/glasses/long/6.html.tmp']
e4a1478e3c1c017945dc8796e8fa8db1        ['https://www.kosmos.com.mx/tienda/catalog/accessories-c-215_216_275_494.html?language=en', 'https://www.kosmos.com.mx/tienda/catalog/accesorios-c-215_216_275_494.html?sort=5a']
```

Note that hashes starting with  "1ab2" and "14d8" contain four URLs each, corresponding to each pair of source-target URLs of duplicates parallel sentences in the original file.

## BENCHMARKS ##

Running on a 28-core (Intel(R) Core(TM) i9-9940X CPU @ 3.30GHz) machine:

* Pairs of sentences processed (fixing and deduplicating) per second:

|  | 8 jobs  |  16 jobs |  28 jobs  |
|---|---|---|---|
| 3M sent | 91K | 143K | 166K |
| 6M sent | 39K | 130K | 150K |
| 9M sent | 26K | 128K | 160K | 


* Time to process a 100 million sentences corpus (28 jobs):
```
real    8m18,519s
user    210m4,782s
sys     6m26,084s
```
(201K sentences/sec)


* Time to deduplicate (`--ignore_characters --ignore_empty --ignore_segmentation`) a 100 million sentences corpus (28 jobs):

```
real    3m15,022s
user    42m32,779s
sys     2m12,951s
```
(513K sent/seg)

(Bifixer Setup & Bifixer Lite. Bifixer Teardown is omitted because it's independent and optional, and can be run afterwards.)
___

![Connecting Europe Facility](https://www.paracrawl.eu/images/logo_en_cef273x39.png)

All documents and software contained in this repository reflect only the authors' view. The Innovation and Networks Executive Agency of the European Union is not responsible for any use that may be made of the information it contains.
