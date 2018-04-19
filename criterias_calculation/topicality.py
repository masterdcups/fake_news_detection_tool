from pytrends.request import TrendReq


def score(keywords):
    s = 0

    pytrends = TrendReq(hl='en-US', tz=360)
    for i in range(len(keywords) // 5):
        pytrends.build_payload(keywords[i * 5:(i * 5) + 5], cat=0, timeframe='today 1-m')
        # Interest Over Time
        interest_over_time_df = pytrends.interest_over_time()

        s += interest_over_time_df.sum().sum()

    m = len(keywords) % 5
    if m != 0:
        pytrends.build_payload(keywords[len(keywords) - m:], cat=0, timeframe='today 1-m')
        # Interest Over Time
        interest_over_time_df = pytrends.interest_over_time()

        s += interest_over_time_df.sum().sum()

    return s


class Topicality:

    @staticmethod
    def get_score(keywords):
        return score(keywords)
