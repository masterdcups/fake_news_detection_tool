

class ScoreNormalization:

    @staticmethod
    def new(criterion, score):
        params = load()
        params = replace_score(params, criterion, score)
        save(params)
        return round(normalize(params, criterion, score), 2)


def save(params):
    file_name = 'app/criterias_calculation/criterias_normalization.txt'

    f = open(file_name, "w")
    for param in params:
        f.write("{}\t{}\t{}\n".format(param[0], param[1], param[2]))


def load():
    file_name = 'app/criterias_calculation/criterias_normalization.txt'
    params = []

    f = open(file_name, "r")
    for line in f:
        tokens = line.split()
        params.append([tokens[0], None if tokens[1] == 'None' else float(tokens[1]),  None if tokens[2] == 'None' else float(tokens[2])])

    return params


def replace_score(params, criterion, score):
    for i in range(len(params)):
        if criterion == params[i][0]:
            if params[i][1] is None or score < params[i][1]:
                params[i][1] = score

            if params[i][2] is None or score > params[i][2]:
                params[i][2] = score

    return params


def normalize(params, criterion, score):
    min = 0
    max = 0

    for i in range(len(params)):
        if criterion == params[i][0]:
            min = params[i][1]
            max = params[i][2]

    max = max - min
    if max == 0.:
        return score
    score = score - min
    score = score * 100 / max
    return score
