import nltk
from statistics import mean
from app.criterias_calculation.senticnet5 import senticnet


class Emotion:

    def __init__(self, text):
        self.text = text

    def get_score(article):
        #nltk.download('averaged_perceptron_tagger')

        # version phrases
        cpt_neg = 0
        cpt_pos = 0
        val_phrases = []

        tokens = nltk.word_tokenize(article)
        tagged_tokens = nltk.pos_tag(tokens)
        for elem in tagged_tokens:
            # print(elem)
            if elem[0] == '.':
                val_phrases.append((cpt_neg,cpt_pos))
                cpt_pos = 0
                cpt_neg = 0
                # print(val_phrases)
            elif elem[0] in senticnet:
                # print(elem, senticnet[elem[0]])
                if senticnet[elem[0]][6] == 'negative':
                    cpt_neg += float(senticnet[elem[0]][7])
                else:
                    cpt_pos += float(senticnet[elem[0]][7])

        cpt_neg = 0
        cpt_pos = 0
        for values in val_phrases:
            cpt_neg += values[0]
            cpt_pos += values[1]
            # print(values, cpt_neg, cpt_pos)

        nb_phrases = len(val_phrases)
        cpt_neg = cpt_neg / nb_phrases
        cpt_pos = cpt_pos / nb_phrases

        score = abs(cpt_neg) + cpt_pos
        print(score)

        return score, abs(cpt_neg), cpt_pos
