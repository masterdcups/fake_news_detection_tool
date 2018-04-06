from pathlib import Path


class ScoreNormalization:

    file_name = 'app/criterias_calculation/criterias_normalization.txt'

    def __init__(self):
        self.params = []
        self.load_params()

    def get_normalize_score(self, criterion, score):
        """

        :param criterion: string, the name of the criterion
        :param score: float, the score to be normelized
        :return:
        """
        self.params = replace_score(self.params, criterion, score)
        return round(normalize(self.params, criterion, score), 2)

    def save(self):
        """
        Save the self.params array into a file
        :return: nothing
        """
        f = open(self.file_name, "w")
        for param in self.params:
            f.write("{}\t{}\t{}\n".format(param[0], param[1], param[2]))
        f.close()

    def load_params(self):
        """
        Load the self.params array from the save file, create the file if not exists
        :return: the params array with each item on the form : [criterion_name, min_score, max_score]
        """
        my_file = Path(self.file_name)
        if not my_file.is_file():
            # if the file does not exist
            self.create_file()

        f = open(self.file_name, "r")
        self.params = []
        for line in f:
            tokens = line.split()
            self.params.append([tokens[0], None if tokens[1] == 'None' else float(tokens[1]),
                           None if tokens[2] == 'None' else float(tokens[2])])
        f.close()

    def create_file(self):
        self.params = [
            ['factuality', None, None],
            ['readability', None, None],
            ['emotion', None, None],
            ['opinion', None, None],
            ['controversy', None, None],
            ['trust', None, None],
            ['technicality', None, None],
            ['topicality', None, None]
        ]
        self.save()


def replace_score(params, criterion, score):
    """
    Replace the min or the max score in the params array
    :param params: params array with min/max scores
    :param criterion: name of the criterion
    :param score: new min or max score
    :return: params array the the new score
    """
    for i in range(len(params)):
        if criterion == params[i][0]:
            if params[i][1] is None or score < params[i][1]:
                params[i][1] = score

            if params[i][2] is None or score > params[i][2]:
                params[i][2] = score

    return params


def normalize(params, criterion, score):
    """
    Given a criterion and an original score, return then normalized score
    :param params: params array with min max infos for each criterias
    :param criterion: name of the criterion
    :param score: original score
    :return: the normalized score
    """
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
