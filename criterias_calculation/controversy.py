import re
import unicodedata
import ssl
from difflib import SequenceMatcher
from stop_words import get_stop_words
from nltk import pos_tag, word_tokenize


def parameterize(string_to_clean, sep='-'):
    parameterized_string = unicodedata.normalize('NFKD', string_to_clean).encode('ASCII', 'ignore').decode()
    parameterized_string = re.sub("[^a-zA-Z0-9\-_]+", sep, parameterized_string)

    if sep is not None and sep is not '':
        parameterized_string = re.sub('/#{re_sep}{2,}', sep, parameterized_string)
        parameterized_string = re.sub('^#{re_sep}|#{re_sep}$', sep, parameterized_string, re.I)

    return parameterized_string.lower()


def get_controversial_tokens():
    controversial_tokens = []
    filename = "criterias_calculation/controversial_topics.txt"

    f = open(filename, "r")
    for line in f:
        controversial_tokens.append(line[:-1])
    f.close()

    return controversial_tokens


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_proper_nouns(tokens):

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    tagged_tokens = pos_tag(tokens)

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
        self.controversial_items = get_controversial_tokens()

    def build_tokens(self):
        tokens = word_tokenize(self.text)
        proper_nouns = get_proper_nouns(tokens)
        self.tokens = tokens + proper_nouns
        self.clean_tokens()

    def find_controversial_tokens(self):

        contro_items = []
        # for each word in text
        for i in range(len(self.tokens)):
            # if the word is in the controversial list
            if self.is_controversial(self.tokens[i]):
                contro_items.append(self.tokens[i])

        return contro_items

    def is_controversial(self, token):
        for item in self.controversial_items:
            #if (similar(item, token)) > 0.9:
            # if parameterize(item) == parameterize(token):
            if str.lower(item) == str.lower(token):
                return True

        return False

    def clean_tokens(self):
        to_be_remove = [',', '“', '”', '’', '.', ':', '—', '–', '-', '|', '[', ']', '(', ')', '$', '!', '‘']
        stop_words = get_stop_words('en')
        new_list = []
        for i in self.tokens:
            if i not in to_be_remove and str.lower(i) not in stop_words:
                new_list.append(i)
        self.tokens = new_list

    def score(self):
        controversial_tokens = self.find_controversial_tokens()
        return len(controversial_tokens) / len(self.tokens)

    @staticmethod
    def call(article):
        c = Controversy(article.text)
        return c.score()



