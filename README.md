Extracts the french-to-english translations from the French Wiktionary

Usage
-----

You can simply use frwiktionary-20140612-euradicfmt.csv (in this repository).

You can also download a dump and process it yourself. Download a frwiktionary
dump from http://dumps.wikimedia.org/frwiktionary/
(frwiktionary-YYYYMMDD-pages-articles.xml.bz2). The last version which is known
to work is
[2014-06-12](https://dumps.wikimedia.org/frwiktionary/20140612/frwiktionary-20140612-pages-articles.xml.bz2).
Next, run:

``` Shell
python3 frwiktionary_extract.py frwiktionary-20140612-pages-articles.xml 2> translation.log | sort | uniq > dictionary.csv
```

Format
------

The bilingual dictionary follows the EurADiC format. Each entry contains the
source word, the source part-of-speech, the label of the dictionary (TR-FR-EN),
the target word, and the target part-of-speech. Here's an example:

``` csv
1000e;J;TR-FR-EN;1000th;J;
100e;J;TR-FR-EN;100th;J;
100 mètres haies;S;TR-FR-EN;100 metre hurdles;S;
baisser;V;TR-FR-EN;debase;V;
abaisser;V;TR-FR-EN;degrade;V;
abruptement;D;TR-FR-EN;abruptly;D;
abruptement;D;TR-FR-EN;steeply;D;
```

Parts of speech
---------------

Only four parts of speech are currently supported:

 * S - nouns
 * V - verbs
 * J - adjectives
 * D - adverbs

Please report an issue or send a pull request for any problem you encounter!
