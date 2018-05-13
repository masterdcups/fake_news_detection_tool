import nltk
from criterias_calculation.AFINN import emotion_tab

class Emotion:

    def __init__(self, text):
        self.text = text

    def get_score(article):

        # version AFINN
        cpt_neg = 0
        cpt_pos = 0
        cpt_mots = 0
        val_phrases = []

        tokens = nltk.word_tokenize(article)
        tagged_tokens = nltk.pos_tag(tokens)
        for elem in tagged_tokens:
            if elem[0] == '.':
                val_phrases.append((cpt_neg / cpt_mots, cpt_pos / cpt_mots))
                cpt_pos = 0
                cpt_neg = 0
            else:
                cpt_mots += 1
                if elem[0] in emotion_tab:
                    if emotion_tab[elem[0]] < 0:
                        cpt_neg += float(emotion_tab[elem[0]])
                    else:
                        cpt_pos += float(emotion_tab[elem[0]])

        cpt_neg = 0
        cpt_pos = 0
        for values in val_phrases:
            cpt_neg += values[0]
            cpt_pos += values[1]

        nb_phrases = len(val_phrases)
        cpt_neg = cpt_neg / nb_phrases
        cpt_pos = cpt_pos / nb_phrases

        score = abs(cpt_neg) + cpt_pos

        return score, (abs(cpt_neg)/score*100.), (cpt_pos/score*100.)
