from django.http import HttpResponse
from django.template import loader
from newspaper import Article
import nltk
from pyfav import get_favicon_url

import sys
import readability



# ----------------------------------------
# python manage.py runserver
# localhost:8000

def score_grade(read_grades_tab_i, vmin, vmax):
    val = read_grades_tab_i[1]
    # print(read_grades_tab_i[0], val)
    if val < vmin:
        val = 0
    elif val > vmax:
        val = 100
    else:
        # Flesch est la seule valeur non inversée par rapport à notre échelle : 0 = difficile, 100 = facile
        if read_grades_tab_i[0] == "FleschReadingEase":
            val = val * 100 / vmax
        else:
            val = 100 - val * 100 / vmax
    # print(val)

    return val

def calcul_score(read_grades_tab, sentence_info_tab):
    tab_score = []
    for i in range(len(read_grades_tab) - 1):
        if read_grades_tab[i][0] == "Kincaid" or read_grades_tab[i][0] == "ARI":
            tab_score.append(score_grade(read_grades_tab[i], 5, 16))
        elif read_grades_tab[i][0] == "FleschReadingEase":
            tab_score.append(score_grade(read_grades_tab[i], 0, 100))
        elif read_grades_tab[i][0] == "LIX":
            tab_score.append(score_grade(read_grades_tab[i], 0, 100))
        elif read_grades_tab[i][0] == "GunningFogIndex" or read_grades_tab[i][0] == "Coleman-Liau":
            if sentence_info_tab[7][1] >= 100:
                tab_score.append(score_grade(read_grades_tab[i], 5, 16))
            else:
                print("La formule de", read_grades_tab[i][0],
                      "ne peut pas être utilisée car il y a moins de 100 mots (", sentence_info_tab[7][1], ").")
        elif read_grades_tab[i][0] == "SMOGIndex":
            if sentence_info_tab[9][1] >= 30:
                tab_score.append(score_grade(read_grades_tab[i], 5, 16))
            else:
                print("La formule de", read_grades_tab[i][0],
                      "ne peut pas être utilisée car il y a moins de 30 phrases (", sentence_info_tab[9][1], ").")
    tab_score.sort()
    print(tab_score)
    n = len(tab_score)
    if n % 2 == 0:
        mediane = (tab_score[n // 2] + tab_score[(n + 1) // 2]) // 2
    else:
        mediane = tab_score[(n + 1) // 2]

    return [mediane, tab_score]

def affichageResults(results):
    read_grades_tab = []
    sentence_info_tab = []

    for niveau1, niveau2 in results.items():
        for titre, valeur in niveau2.items():
            if niveau1 == "readability grades":
                read_grades_tab.append([titre, valeur])
            elif niveau1 == "sentence info":
                sentence_info_tab.append([titre, valeur])

    mediane, tab_normalized_score = calcul_score(read_grades_tab, sentence_info_tab)
    taux_accord = calcul_taux_accord(tab_normalized_score, mediane)

    return mediane, taux_accord

def calcul_tab_categorie(tab_normalized_score, moyenne):
    pas = 10
    tab = []
    # calcul des categories en fonction de la moyenne
    moyenne_initiale = moyenne
    tab.insert(0, [moyenne - pas, moyenne + pas])
    while moyenne > 0:
        moyenne -= 20
        tab.insert(0, [moyenne - pas, moyenne + pas])
    moyenne_initiale += 20
    while moyenne_initiale < 100:
        tab.append([moyenne_initiale - pas, moyenne_initiale + pas])
        moyenne_initiale += 20

    len_tab = len(tab)
    for i in range(len_tab):
        tab[i] = [tab[i][0], tab[i][1], 0, 0]

    # calcul du nombre de valeur dans chaque categorie
    for i in range(len(tab_normalized_score)):
        for j in range(len_tab):
            if tab_normalized_score[i] > tab[j][0] and tab_normalized_score[i] < tab[j][1]:
                tab[j][2] += 1

    print("tab categories :",tab)
    return tab

def calcul_taux_accord(tab_normalized_score, moyenne):
    tab = calcul_tab_categorie(tab_normalized_score,moyenne)
    n = len(tab_normalized_score)

    Pe = Pi = 0
    for i in range(len(tab)):
        Pj = tab[i][2] / n
        tab[i][3] = Pj
        Pe += Pj * Pj
        Pi += tab[i][2] * tab[i][2]
    Pi = Pi / (n * (n -1))
    K = (Pi - Pe) / (1 - Pe)

    #print(K)

    return K * 100

# ----------------------------------------


def index(request):
    url = request.GET.get('q', None)
    if url != None:
        article = Article(url)
        article.download()
        article.parse()

        nltk.download('punkt')
        article.nlp()
        results = readability.getmeasures(article.text, lang='en')
        # scoreReadability = affichageResults(results)
        scoreReadability, taux_accord = affichageResults(results)
        pcread = round(scoreReadability,3), round(taux_accord,3)
        # -------
    else:
        article = None
        # scoreReadability = None
        pcread = None



    params = [
        ['factuality', None],
        ['readability', pcread],
        # ['readability', scoreReadability],
        ['virality', None],
        ['emotion', None],
        ['opinion', None],
        ['controversy', None],
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
