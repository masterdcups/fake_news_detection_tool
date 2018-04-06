from app.criterias_calculation.controversy import Controversy
from app.criterias_calculation.readability import Readability
from app.criterias_calculation.score_normalization import ScoreNormalization
from app.criterias_calculation.technicality import Technicality
from app.criterias_calculation.trust import Trust


def score_format(score):
    return round(score, 2)


class ScoreCalculation:

    def __init__(self, article, url):
        readability_score, readability_taux_accord = Readability.get_score(article.text)
        controversy_score = Controversy.call(article)
        technicality_score = Technicality.get_score(article.text)
        trust_score, trust_confidence = Trust.call(url)

        self.params = [
            ['factuality', None, None, True],
            ['readability', readability_score,
             "Agreement rate : {}%".format(score_format(readability_taux_accord)), False],
            ['emotion', None, None, True],
            ['opinion', None, None, True],
            ['controversy', controversy_score, None, True],
            ['trust', score_format(trust_score),
             "Confidence score : {}%".format(score_format(trust_confidence)), False],
            ['technicality', technicality_score, None, True],
            ['topicality', None, None, True]
        ]

    def get_normalized_params(self):
        """
        Return an params array with normalized score
        :return: params array with each item on the form :
                 [criterion_name, score, description, to_be_normalized]
        """
        score_normalization = ScoreNormalization()

        for p in self.params:
            if p[3] and p[1] is not None:
                p[1] = score_normalization.get_normalize_score(p[0], p[1])

        score_normalization.save()

        return self.params

    def get_global_score(self):
        """
        To be called after get_normalized_params()
        :return: Return the global score of all criterions
        """
        score = 0
        nb_criterias_implemented = 0

        for p in self.params:
            if p[1] is not None:
                score += p[1]
                nb_criterias_implemented += 1
        return score_format(score / nb_criterias_implemented)


