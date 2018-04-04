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
             "Agreement rate : {}%".format(score_format(readability_taux_accord * 100.)), True],
            ['emotion', None, None, True],
            ['opinion', None, None, True],
            ['controversy', controversy_score, None, True],
            ['trust', score_format(trust_score), "Confidence score : {}%".format(score_format(trust_confidence)), False],
            ['technicality', technicality_score, None, True],
            ['topicality', None, None, True]
        ]

    def get_normalized_params(self):
        score_normalization = ScoreNormalization()

        print(self.params)

        for p in self.params:
            if p[3] and p[1] is not None:
                p[1] = score_normalization.get_normalize_score(p[0], p[1])

        score_normalization.save()

        print(self.params)

        return self.params

    def get_global_score(self):
        print(self.params)
        score = 0
        nb_criterias_implemented = 0
        for p in self.params:
            if p[1] is not None:
                score += p[1]
                nb_criterias_implemented += 1
        return score_format(score / nb_criterias_implemented)


