from pytrends.request import TrendReq
#import pandas as pd

def score(keywords):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe='today 1-m')
    # Interest Over Time
    interest_over_time_df = pytrends.interest_over_time()

    score = interest_over_time_df.sum().sum()

    return score


class Topicality:

    def get_score(keywords):
        return score(keywords)

