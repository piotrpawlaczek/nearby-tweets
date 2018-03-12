"""
Official Twitter API is annoying to work with, has lots of limitations and requires
credentials you have to apply for. As don't want to be so frustratingly locked down we support both
resverse-engineered and official version.
"""
import re
import json
import lxml
import urllib
import random
import logging
import requests

from twitter import Api as TwitterApi

from lxml import etree
from shapely.geometry import Polygon
from pyquery import PyQuery
from requests import Session
from fake_useragent import UserAgent
from urllib.parse import quote_plus

from config import Config

from typing import Dict, Iterable, Iterator, Any, List, Union


MAP_RESPONSE = {
    "geometry": {"type": "Point", "coordinates": []},
    "type": "Feature", "properties": {}, "tweet": ""
}


class Api(object):
    """Nearby api api(s)"""
    OFFICIAL = 'official'
    REVERSE_ENGINEERED = 'reverse-engineered'

    @classmethod
    def get_official(cls) -> '_ApiOfficial':
        api = TwitterApi(
            consumer_key=Config.CONSUMER_KEY,
            consumer_secret=Config.CONSUMER_SECRET,
            access_token_key=Config.ACCESS_TOKEN,
            access_token_secret=Config.ACCESS_TOKEN_SECRET
        )
        api.VerifyCredentials()
        return _ApiOfficial(api)

    @classmethod
    def get_reversed(cls) -> '_ApiReversedEngineered':
        return _ApiReverseEngineered()

    @classmethod
    def get_default(cls) -> Union['_ApiOfficial', '_ApiReversedEngineered']:
        if all([Config.CONSUMER_KEY,
                Config.CONSUMER_SECRET,
                Config.ACCESS_TOKEN,
                Config.ACCESS_TOKEN_SECRET]):
            return cls.get_official()
        return cls.get_reversed()


class ApiBase(object):

    @property
    def is_official(self):
        return self.channel == Api.OFFICIAL


class _ApiOfficial(ApiBase):
    """Official Twitter API"""
    channel = Api.OFFICIAL

    def __init__(self, entry_point: Any) -> None:
        logging.warning('Using official version!')
        self.streaming_api = entry_point.GetStreamFilter

    def get_tweets(self, where: List, lang: List=['en'], pages: int=25) -> Iterator[str]:
        """Where: comma separated coordinates in polygon format"""
        for tweet in self.streaming_api(locations=where, languages=lang):
            yield tweet['text']

    def get_tweets_map(self, where: List, lang: List=['en'], pages: int=25) -> Iterator[dict]:
        """Where: comma separated coordinates in polygon format"""
        for tweet in self.streaming_api(locations=where, languages=lang):
            MAP_RESPONSE['tweet'] = tweet['text']
            polygon = Polygon(tweet['place']['bounding_box']['coordinates'][0])
            centroid = polygon.representative_point().coords[0]
            MAP_RESPONSE['geometry']['coordinates'] = list(centroid)[::-1]
            yield MAP_RESPONSE


class _ApiReverseEngineered(ApiBase):
    """Reversed engineered API"""
    channel = Api.REVERSE_ENGINEERED

    def __init__(self):
        logging.warning('Using reverse-engineered version!')
        self.session = Session()  # A consumable session for connection pooling
        self.fk_user_agent = UserAgent()  # A fake user-agent

    def get_tweets(self, where: List=['me'], lang: List=['en'], pages: int=25) -> Iterator[str]:
        """Gets tweets nearby 'where', via the Twitter front-end API."""
        where = quote_plus(where[0])
        lang = lang[0]
        url = f'https://twitter.com/i/search/timeline?q=near%3A%22{where}%22%20within%3A5mi&src=typd&include_available_features=1&include_entities=1'

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': f'https://twitter.com/search?q=near%3A%22{where}%22%20within%3A5mi&src=typd',
            'User-Agent': self.fk_user_agent.random,  # provide a random user agent
            'X-Twitter-Active-User': 'yes',
            'X-Requested-With': 'XMLHttpRequest',
            'X-asset-version': 'dfe035',
            'X-push-state-request': 'true'
        }

        def get_tweets_from_json(tree: Iterable) -> Iterator[str]:
            """Generate tweet-texts from the html page."""
            html_tweets = PyQuery(tree)('.tweet-text')
            for tweet in html_tweets:
                yield tweet.text

        def get_pagination(tree: Iterable) -> Dict[str, str]:
            """Determine last and first tweet from the html page."""
            selector = PyQuery(tree)('.stream-item')
            return dict(selector[0].items())['data-item-id'], dict(selector[-1].items())['data-item-id']

        def gen_tweets(pages: int) -> Iterator[str]:
            """HTML-based tweets generator."""
            req = self.session.get(url, headers=headers, params={'l': f'{lang}'})
            while pages > 0:
                try:
                    tree = etree.HTML(req.json()['items_html'])
                    first_tweet, last_tweet = get_pagination(tree)
                    max_position = f'TWEET-{last_tweet}-{first_tweet}'

                    for tweet in get_tweets_from_json(tree):
                        if tweet:
                            yield re.sub('http', ' http', tweet, 1)

                    req = self.session.get(
                      url, params={'max_position': max_position, 'l': f'{lang}'}, headers=headers
                    )
                except (json.decoder.JSONDecodeError, KeyError) as error:
                    logging.error(f'{where} -> {error}')
                finally:
                    pages += -1

        yield from gen_tweets(pages)

    def get_tweets_map(self, where: List=['me'], lang: List=['en'], pages: int=25) -> Iterator[dict]:
        """As twitter internal API does not provide tweet coordinates we will only shake the original ones."""
        lang = lang[0]
        if 'geocode' not in where[0]:
            resp = requests.get('https://freegeoip.net/json').json()
            longi, latit = float(resp['longitude']), float(resp['latitude'])
        else:
            geo1, latit, longi, geo4 = map(float, where[0].split(':')[-1].split(','))

        for tweet in self.get_tweets(where, lang, pages):
            geo1, geo2 = random.uniform(latit, latit + 0.09), random.uniform(longi, longi + 0.09)
            MAP_RESPONSE['geometry']['coordinates'] = [geo1, geo2]
            MAP_RESPONSE['tweet'] = tweet
            yield MAP_RESPONSE
