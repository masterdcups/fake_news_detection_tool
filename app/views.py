from django.http import HttpResponse
from django.template import loader
from newspaper import Article
import nltk
from pyfav import get_favicon_url

from app.criterias_calculation.score_calculation import ScoreCalculation


def index(request):
    url = request.GET.get('q', None)
    article = None
    params = None
    score = None

    if url is not None:
        article = Article(url)
        article.download()
        article.parse()

        nltk.download('punkt')
        article.nlp()

        score_calc = ScoreCalculation(article, url)
        params = score_calc.get_normalized_params()
        score = score_calc.get_global_score()

    favicon_url = get_favicon_url(url) if url is not None else None

    template = loader.get_template('app/index.html')
    context = {
        'article': article,
        'authors': ', '.join(article.authors) if article is not None else '',
        'params': split_list(params),
        'score': score,
        'favicon_url': favicon_url
    }
    return HttpResponse(template.render(context, request))


def split_list(list_item):
    assert type(list_item) == list

    if list_item is None:
        return None

    size = len(list_item)
    p1 = []
    p2 = []

    if size % 2 == 0:
        p1 = list_item[:int(size / 2)]
        p2 = list_item[int(size / 2):]
    else:
        p1 = list_item[:int((size + 1) / 2)]
        p2 = list_item[int((size + 1) / 2):]

    return [p1, p2]

