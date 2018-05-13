from criterias_calculation.controversy import Controversy
from criterias_calculation.emotion import Emotion
from criterias_calculation.factuality_opinion import FactualityOpinion
from criterias_calculation.score_normalization import ScoreNormalization
from criterias_calculation.sql_manager import SQLManager
from criterias_calculation.technicality import Technicality
from criterias_calculation.topicality import Topicality
from criterias_calculation.trust import Trust
from criterias_calculation.readability import Readability


def score_format(score):
    return round(score, 2)


def params_to_dict(params):
    dictionary = {}
    for p in params:
        dictionary[p[0]] = {'score': p[1], 'desc': p[2]}

    return dictionary


def tuple_to_params(sql_tuple):
    return [
        ['factuality', sql_tuple[2], sql_tuple[10], True],
        ['readability', sql_tuple[3], sql_tuple[11], False],
        ['emotion', sql_tuple[4], sql_tuple[12], True],
        ['opinion', sql_tuple[5], sql_tuple[13], True],
        ['controversy', sql_tuple[6], sql_tuple[14], True],
        ['trust', sql_tuple[7], sql_tuple[15], False],
        ['technicality', sql_tuple[8], sql_tuple[16], True],
        ['topicality', sql_tuple[9], sql_tuple[17], True]
    ]


class ScoreCalculation:

    def __init__(self, article, url):
        self.article = article
        self.url = url
        self.sql_manager = SQLManager()

        if self.sql_manager.article_exists(url):
            self.params = tuple_to_params(self.sql_manager.get_scores(url))
        else:
            self.calculate_criteria()

    def calculate_criteria(self):
        readability_score, readability_agreement_rate = Readability.get_score(self.article.text)
        controversy_score = Controversy.call(self.article)
        technicality_score = Technicality.get_score(self.article.text)
        trust_score, trust_confidence = Trust.call(self.url)
        fact_score, opinion_score, fact_sents, opinion_sents, nb_sents = FactualityOpinion.classify(self.article.text)
        emotion_score, nb_neg, nb_pos = Emotion.get_score(self.article.text)
        self.article.nlp()
        topicality_score = Topicality.get_score(self.article.keywords)

        self.params = [
            ['factuality', fact_score, "{} fact sentences found on {} total sentences".format(fact_sents, nb_sents),
             True],
            ['readability', readability_score,
             "Agreement rate : {}%\nAverage of the differents readability formulas, computing ratio between number of "
             "syllables, word length, sentence length, number of words, number of complex words and sentences.".format(
                 score_format(readability_agreement_rate)), False],
            ['emotion', emotion_score,
             "Counting number of emotional word in a sentence, multiplied with a valuation of the word\nNegative "
             "emotion : {}%, positive emotion : {}%".format(score_format(nb_neg), score_format(nb_pos)), True],
            ['opinion', opinion_score,
             "{} opinion sentences found on {} total sentences".format(opinion_sents, nb_sents), True],
            ['controversy', controversy_score,
             "Density of known controversial issues (form the Wikipedia article List_of_controversial_issues) in the "
             "text",
             True],
            ['trust', score_format(trust_score),
             "Confidence score : {}%\nUse of the API provided by www.mywot.com about trust of the article website "
             "domain".format(score_format(trust_confidence)), False],
            ['technicality', technicality_score, "Rate of technical lexical noun-phrases in the article", True],
            ['topicality', topicality_score,
             "Number of top searches of keywords of the article during the last month (on Google)",
             True]
        ]

        self.sql_manager.insert_new_scores(self.url, params_to_dict(self.params))

    def get_normalized_params(self):
        """
        Return an params array with normalized score
        :return: params array with each item on the form :
                 [criterion_name, score, description, to_be_normalized]
        """
        score_normalization = ScoreNormalization(self.sql_manager)

        for p in self.params:
            if p[3]:
                if p[1] is not None:
                    p[1] = score_normalization.get_normalize_score(p[0], p[1])
            else:
                p[1] = score_format(p[1])

        self.sql_manager.save()

        return self.params

    def get_global_score(self):
        """
        To be called after get_normalized_params()
        :return: Return the global score of all criteria
        """
        score = 0
        nb_criteria_implemented = 0

        for p in self.params:
            if p[1] is not None:
                score += p[1]
                nb_criteria_implemented += 1
        return score_format(score / nb_criteria_implemented)
