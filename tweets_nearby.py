"""
Official Twitter API is annoying to work with, has lots of limitations and requires
credentials you have to apply for. As don't want to be so frustratingly locked down here is some
resversed engineered version.
"""
import re
import json
import lxml
import urllib
import random
import logging
import requests

from lxml import etree
from pyquery import PyQuery
from requests import Session
from fake_useragent import UserAgent

from typing import Dict, Iterable, Iterator


session = Session()  # A consumable session for connection pooling
fk_user_agent = UserAgent()  # A fake user-agent


def get_tweets(where: str='me', lang: str='en', pages: int=25) -> Iterator[str]:
    """Gets tweets nearby 'where', via the Twitter front-end API."""
    url = f'https://twitter.com/i/search/timeline?q=near%3A%22{where}%22%20within%3A5mi&src=typd&include_available_features=1&include_entities=1'

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': f'https://twitter.com/search?q=near%3A%22{where}%22%20within%3A5mi&src=typd',
        'User-Agent': fk_user_agent.random,  # provide a random user agent
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
        req = session.get(url, headers=headers, params={'l': f'{lang}'})
        while pages > 0:
            try:
                tree = etree.HTML(req.json()['items_html'])
                first_tweet, last_tweet = get_pagination(tree)
                max_position = f'TWEET-{last_tweet}-{first_tweet}'

                for tweet in get_tweets_from_json(tree):
                    if tweet:
                        yield re.sub('http', ' http', tweet, 1)

                req = session.get(
                    url, params={'max_position': max_position, 'l': f'{lang}'}, headers=headers
                )
            except (json.decoder.JSONDecodeError, KeyError) as error:
                logging.error(f'{where} -> {error}')
            finally:
                pages += -1

    yield from gen_tweets(pages)


def get_tweets_map(where: str='me', lang: str='en', pages: int=25) -> Iterator[dict]:
    """As twitter internal API does not provide tweet coordinates we will only shake the original ones."""
    if 'geocode' not in where:
        resp = requests.get('https://freegeoip.net/json').json()
        longi, latit = float(resp['longitude']), float(resp['latitude'])
    else:
        where = urllib.parse.unquote(where)
        longi, latit = map(float, where.split(':')[-1].split(','))

    map_response = {
        "geometry": {"type": "Point", "coordinates": []}, "type": "Feature", "properties": {}, "tweet": ""
    }
    for tweet in get_tweets(where, lang, pages):
        geo1, geo2 = random.uniform(latit, latit + 0.09), random.uniform(longi, longi + 0.09)
        map_response['geometry']['coordinates'] = [geo1, geo2]
        map_response['tweet'] = tweet
        yield map_response
