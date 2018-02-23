import nltk
import re
import unicodedata
import ssl


def parameterize(string_to_clean, sep='-'):
    parameterized_string = unicodedata.normalize('NFKD', string_to_clean).encode('ASCII', 'ignore').decode()
    parameterized_string = re.sub("[^a-zA-Z0-9\-_]+", sep, parameterized_string)

    if sep is not None and sep is not '':
        parameterized_string = re.sub('/#{re_sep}{2,}', sep, parameterized_string)
        parameterized_string = re.sub('^#{re_sep}|#{re_sep}$', sep, parameterized_string, re.I)

    return parameterized_string.lower()


def remove_ponctuation(list):
    while ',' in list: list.remove(',')
    while '“' in list: list.remove('“')
    while '”' in list: list.remove('”')
    while '’' in list: list.remove('’')
    while '.' in list: list.remove('.')
    while ':' in list: list.remove(':')
    while '—' in list: list.remove('—')
    return list


def read_data(filename):

    data = []

    with open(filename, "r") as f:
        line = f.readline().strip()
        while line:
            data.append(parameterize(line))
            line = f.readline().strip()

    return data


class Controversy:

    def __init__(self, text):
        self.text = text

    @staticmethod
    def call(article):
        text = article.title
        text += ' - ' + article.text
        c = Controversy(text)
        controversial_topics = read_data("app/criterias_calculation/controversial_topics.txt")
        print(controversial_topics)
        proper_nouns = c.get_proper_nouns()
        print(proper_nouns)
        tokens = nltk.word_tokenize(c.text)
        tokens = remove_ponctuation(tokens)
        tokens = tokens + proper_nouns

        nb_controversial_topics = 0
        contro_items = []
        for i in range(len(tokens)):
            # print(parameterize(tokens[i]))
            if parameterize(tokens[i]) in controversial_topics:
                nb_controversial_topics += 1
                contro_items.append(tokens[i])

        return c.score(nb_controversial_topics, tokens)

    def score(self, nb_controversial_topics, all_tokens):
        return nb_controversial_topics / len(all_tokens) * 1000

    def get_proper_nouns(self):

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        tagged_tokens = nltk.pos_tag(nltk.word_tokenize(self.text))

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