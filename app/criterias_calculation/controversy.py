import nltk
import re
import unicodedata
import ssl
from difflib import SequenceMatcher
from stop_words import get_stop_words


def parameterize(string_to_clean, sep='-'):
    parameterized_string = unicodedata.normalize('NFKD', string_to_clean).encode('ASCII', 'ignore').decode()
    parameterized_string = re.sub("[^a-zA-Z0-9\-_]+", sep, parameterized_string)

    if sep is not None and sep is not '':
        parameterized_string = re.sub('/#{re_sep}{2,}', sep, parameterized_string)
        parameterized_string = re.sub('^#{re_sep}|#{re_sep}$', sep, parameterized_string, re.I)

    return parameterized_string.lower()


def build_controversial_map():
    map = {}
    filename = "app/criterias_calculation/controversial_topics.txt"

    f = open(filename, "r")
    for line in f:
        map[line.split()[0]] = []

    return map


def load_anchor_text_in_map(map):
    filename = "app/criterias_calculation/anchortext.txt"

    f = open(filename, "r")
    for line in f:
        parts = line.split(" ")
        if len(parts) > 2:
            page_id = parts[1][1:len(parts[1]) - 1]
            anchor = " ".join(parts[2:]).replace("\n", "")
            anchor = anchor[1:len(anchor) - 1]

            if page_id in map:
                map[page_id].append(anchor)

    return map


def controversial_map_with_anchor_text():
    map = build_controversial_map()
    return load_anchor_text_in_map(map)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_proper_nouns(tokens):

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    tagged_tokens = nltk.pos_tag(tokens)

    res = []
    local_word = ''
    for i in range(len(tagged_tokens)):
        word = tagged_tokens[i]
        prev = tagged_tokens[i - 1]
        next = tagged_tokens[i + 1] if i < len(tagged_tokens) - 1 else ('', None)

        if word[1] == 'NNP' and (prev[1] == 'NNP' or next[1] == 'NNP'):
            local_word += ' ' + word[0]
        else:
            if local_word != '':
                res.append(local_word.lstrip())
            local_word = ''

    return res


class Controversy:

    def __init__(self, text):
        self.text = text
        self.build_tokens()
        self.controversial_items = controversial_map_with_anchor_text()

    def build_tokens(self):
        tokens = nltk.word_tokenize(self.text)
        proper_nouns = get_proper_nouns(tokens)
        self.tokens = tokens + proper_nouns
        self.clean_tokens()

    def find_controversials_tokens(self):

        contro_items = []
        for i in range(len(self.tokens)):
            if self.is_controversial(self.tokens[i]):
                contro_items.append(self.tokens[i])

        return contro_items

    def is_controversial(self, token):
        for key, value in self.controversial_items.items():
            for j in range(len(self.controversial_items[key])):
                # if (similar(self.controversial_items[key][j], token)) > 0.8:
                if parameterize(self.controversial_items[key][j]) == parameterize(token):
                    return True

        return False

    def clean_tokens(self):
        to_be_remove = [',', '“', '”', '’', '.', ':', '—', '–', '-', '|', '[', ']', '(', ')', '$', '!']
        stop_words = get_stop_words('en')
        new_list = []
        for i in self.tokens:
            if i not in to_be_remove and str.lower(i) not in stop_words:
                new_list.append(i)
        self.tokens = new_list

    def score(self):
        controversial_tokens = self.find_controversials_tokens()
        return len(controversial_tokens) / len(self.tokens)

    @staticmethod
    def call(article):
        c = Controversy(article.text)
        return c.score()



