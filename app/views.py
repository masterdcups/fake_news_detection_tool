import functools

from django.http import HttpResponse
from django.template import loader
from newspaper import Article
import nltk
from pyfav import get_favicon_url

from app.criterias_calculation.controversy import Controversy
from app.criterias_calculation.readability import Readability
from app.criterias_calculation.score_normalization import ScoreNormalization
from app.criterias_calculation.technicality import Technicality
from app.criterias_calculation.trust import Trust


def score_format(score):
    return round(score, 2)


def index(request):
    url = request.GET.get('q', None)
    article = None
    params = None
    score = None

    if url != None:
        article = Article(url)
        article.download()
        article.parse()

        nltk.download('punkt')
        article.nlp()

        readability_score, readability_taux_accord = Readability.get_score(article.text)
        controversy_score = Controversy.call(article)
        technicality_score = Technicality.getTechnicalityScore(article.text)
        trust_score, trust_confidence = Trust.call(url)

        params = [
            ['factuality', None, None],
            ['readability', ScoreNormalization.new('readability', score_format(readability_score)), "Agreement rate : {}%".format(score_format(readability_taux_accord*100.))],
            ['emotion', None, None],
            ['opinion', None, None],
            ['controversy', ScoreNormalization.new('controversy', score_format(controversy_score)), None],
            ['trust', score_format(trust_score), "Confidence score : {}%".format(score_format(trust_confidence))],
            ['technicality', ScoreNormalization.new('technicality', score_format(technicality_score)), None],
            ['topicality', None, None]
        ]

        # todo : faire un truc plus générique avec quand params[3] = 1 faire 100-params[1]
        score = score_format((readability_score + controversy_score + technicality_score + trust_score) / 4)


    favicon_url = get_favicon_url(url) if url is not None else None

    template = loader.get_template('app/index.html')
    context = {
        'article': article,
        'authors': ', '.join(article.authors) if article != None else '',
        'params': split_list(params),
        'score': score,
        'favicon_url': favicon_url
    }
    return HttpResponse(template.render(context, request))


def split_list(list):
    if list is None:
        return None

    size = len(list)
    p1 = []
    p2 = []

    if size % 2 == 0:
        p1 = list[:int(size / 2)]
        p2 = list[int(size / 2):]
    else:
        p1 = list[:int((size + 1) / 2)]
        p2 = list[int((size + 1) / 2):]

    return [p1, p2]

