"""
Unit tests
"""
import types

from tweets_nearby import get_tweets
from tweets_nearby import get_tweets_map


def test_get_tweets():
    """Test if get_tweets generator actually generate some tweets."""
    tweets = get_tweets(where='Dublin', lang='en', pages=1)
    assert isinstance(tweets, types.GeneratorType)
    tweets = tuple(tweets)  # generatre some tweets
    assert len(tweets)   # check if there are some tweets
    for tweet in tweets:
        assert isinstance(tweet, str)  # check if tweets are readable


def test_get_tweets_map():
    """Test if get_tweets generator actually generate some tweets."""
    tweets = get_tweets_map(where='Warsaw', lang='en', pages=1)
    assert isinstance(tweets, types.GeneratorType)
    tweets = tuple(tweets)  # generatre some tweets
    assert len(tweets)  # check if there are some tweets
    for tweet in tweets:
        assert isinstance(tweet, dict)  # check if tweets are readable
        assert 'tweet' in tweet
        assert 'coordinates' in tweet['geometry']
