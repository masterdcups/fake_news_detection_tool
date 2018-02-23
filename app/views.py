from django.http import HttpResponse
from django.template import loader
from newspaper import Article
import nltk
from pyfav import get_favicon_url

from app.criterias_calculation.controversy import Controversy


def score_format(score):
    return round(score, 2)


def index(request):
    url = request.GET.get('q', None)
    if url != None:
        article = Article(url)
        article.download()
        article.parse()

        nltk.download('punkt')
        article.nlp()

    else:
        article = None

    params = [
        ['factuality', None],
        ['readability', None],
        ['virality', None],
        ['emotion', None],
        ['opinion', None],
        ['controversy', score_format(Controversy.call(article))],
        ['authority/credibility/trust', None],
        ['technicality', None],
        ['topicality', None]
    ]

    score = None

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
