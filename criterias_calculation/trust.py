import urllib.request
from urllib.parse import urlparse
import json


class Trust:

    def __init__(self, url):
        self.url = url
        self.domain = self.get_domain()

    @staticmethod
    def call(url):
        trust = Trust(url)
        return trust.make_request()

    def make_request(self):
        api_key = "c6954eeb25d45fe8258ab87b121fe28804e93fcf"
        content = urllib.request.urlopen(
            "http://api.mywot.com/0.4/public_link_json2?hosts=" + self.domain + "/&key=" + api_key).read().decode("utf-8")
        content = json.loads(content)
        trustworthiness = content[self.domain[:(len(self.domain)-1)]]['0']
        trustworthiness_confidence = trustworthiness[1]
        return float(trustworthiness[0]), float(trustworthiness_confidence)

    def get_domain(self):
        parsed_uri = urlparse(self.url)
        d = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        d = d.replace('http://', '')
        d = d.replace('https://', '')
        return d

