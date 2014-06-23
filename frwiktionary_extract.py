#!/usr/bin/env python3

import sys
import xml.sax
from io import StringIO
import re
import locale

# TODO handle full complexity of {{trad}}
# https://fr.wiktionary.org/wiki/Mod%C3%A8le:trad
# TODO add other parts-of-speech (search the log for "unused pos")
# TODO support cross part-of-speech translations?

pos_dictionary = {
    'adv': [
        'adv', 'adverbe',
        # less than 10
        'adverbe relatif', 'adverbe interrogatif',
    ],
    'adj': [

        'adj', 'adjectif', 'adjectif numéral', 'adjectif indéfini',
        'adjectif démonstratif', 'adjectif possessif',
        # less than 10
        'adjectif interrogatif', 'adjectif exclamatif', 'adj-dém',
    ],
    'noun': [
        'nom', 'substantif', 'nom commun',
        'nom-fam',
        'prénom', 'nom de famille',
        'nom-pr', 'nom propre',
    ],
    'verb': [
        'verb', 'verbe', 'verbe pronominal'
    ]
}

euradic_pos = {
    'noun': 'S',
    'adj': 'J',
    'verb': 'V',
    'adv': 'D'
}


all_pos = []
for p in pos_dictionary:
    all_pos.extend(pos_dictionary[p])


def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


class WikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.content = ''

    @overrides(xml.sax.ContentHandler)
    def endElement(self, name):
        if name == "title":
            self.title = self.content
        elif name == "text":
            if not self.title.startswith('Wiktionnaire:'):
                add_translation(self.title, self.content)

    @overrides(xml.sax.ContentHandler)
    def startElement(self, name, attrs):
        self.content = ""

    @overrides(xml.sax.ContentHandler)
    def characters(self, content):
        self.content += content


def with_translation():
    articles = {}
    for page in mediawiki.findall(ns("page")):
        page_title = page.find(ns("title")).text
        wiki_text = page.find("{}/{}".format(ns("revision"), ns("text"))).text
        for line in StringIO(wiki_text):
            if "{{trad" in line:
                articles[page_title] = wiki_text

    return articles


def french_section(wiki_text):
    french_text = ''
    french = False
    for line in StringIO(wiki_text):
        if '{{langue|fr}}' in line:
            french = True
        elif '{{langue|' in line:
            french = False

        if french:
            french_text += line

    return french_text


def part_of_speechs(page_title, french_text):
    global all_pos

    pos_texts = []
    current_pos = None

    for line in StringIO(french_text):
        line = line.strip()
        if line.startswith('=== {{S|'):
            try:
                possible_pos = re.match('=== {{S\|([^|]+)\|', line).group(1)
                if possible_pos in all_pos:
                    all_pos.remove(possible_pos)

                found_pos = False
                for pos in pos_dictionary:
                    if possible_pos in pos_dictionary[pos]:
                        found_pos = True
                        current_pos = pos
                        pos_texts.append({"pos": pos, "text": ""})
                if not found_pos:
                    print(
                        'unknown pos ;{}; - {}'.format(possible_pos, page_title),
                        file=sys.stderr)
            except AttributeError:

                expected_errors = ['étymologie', 'références', 'voir aussi',
                                   'prononciation', 'anagrammes']
                if not [error for error in expected_errors if error in line]:
                    print('no pos ;{}; - {}'.format(line, page_title), file=sys.stderr)

        if current_pos:
            pos_texts[-1]['text'] += line + '\n'

    return pos_texts


def translations(pos_text):
    for line in StringIO(pos_text):
        line = line.strip()
        if '{{T|en}}' in line and 'ébauche-trad' not in line:
            for trad in re.findall('{{trad[+-]?\|en\|.+?}}', line, flags=re.UNICODE):
                trad = trad[2:-2]  # remove braces
                splits = trad.split('|')
                yield splits[2]


def add_translation(page_title, wiki_text):
    french_text = french_section(wiki_text)
    pos_texts = part_of_speechs(page_title, french_text)

    for pos in pos_texts:
        for t in translations(pos['text']):
            print("{0};{1};TR-FR-EN;{2};{1};".format(page_title, euradic_pos[pos['pos']], t))

parser = xml.sax.make_parser()
parser.setContentHandler(WikiHandler())
xmlfile = open(sys.argv[1])
parser.parse(xmlfile)
print('unused pos ', all_pos, file=sys.stderr)
