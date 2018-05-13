from flask import Flask, render_template, request
from newspaper import Article
from pyfav import get_favicon_url
from criterias_calculation.score_calculation import ScoreCalculation
import httplib2

httplib2._MAXHEADERS = 1000
app = Flask(__name__)



@app.route('/')
def index():
    url = request.args.get('q')
    article = None
    params = None
    score = None

    if url is not None:
        article = Article(url)
        article.download()
        article.parse()

        score_calc = ScoreCalculation(article, url)
        params = score_calc.get_normalized_params()
        score = score_calc.get_global_score()

    favicon_url = get_favicon_url(url) if url is not None else None

    return render_template('index.html',
                           article=article,
                           authors=', '.join(article.authors) if article is not None else '',
                           params=split_list(params),
                           score=score,
                           favicon_url=favicon_url)


def split_list(list_item):
    assert type(list_item) == list or list_item is None

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


if __name__ == '__main__':
    app.run()

