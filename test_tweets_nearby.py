"""
Unit tests
"""
import types

from tweets_nearby import Api


def test_get_tweets():
    """Test if get_tweets generator actually generate some tweets."""
    get_tweets = Api.get_reversed().get_tweets
    tweets = get_tweets(where=['Dublin'], lang=['en'], pages=1)
    assert isinstance(tweets, types.GeneratorType)
    tweets = tuple(tweets)  # generatre some tweets
    assert len(tweets)   # check if there are some tweets
    for tweet in tweets:
        assert isinstance(tweet, str)  # check if tweets are readable


def test_get_tweets_map():
    """Test if get_tweets_map generator actually generate some tweets with coordinates."""
    get_tweets_map = Api.get_reversed().get_tweets_map
    tweets = get_tweets_map(where=['Warsaw'], lang=['en'], pages=1)
    assert isinstance(tweets, types.GeneratorType)
    tweets = tuple(tweets)  # generatre some tweets
    assert len(tweets)  # check if there are some tweets
    for tweet in tweets:
        assert isinstance(tweet, dict)  # check if tweets are readable
        assert 'tweet' in tweet
        assert 'coordinates' in tweet['geometry']


def test_get_tweets_official():
    """Test if get_tweets generator actually generate some tweets."""
    api = Api.get_default()
    if api.channel == Api.OFFICIAL:
        assert api.is_official
        tweets = api.get_tweets(where=['-122.75,36.8,-121.75,37.8'], lang=['en'], pages=1)
        assert isinstance(tweets, types.GeneratorType)
        tweet = next(tweets)  # generatre some tweets
        assert isinstance(tweet, str)  # check if tweets are readable


def test_get_tweets_map_official():
    """Test if get_tweets_map generator actually generate some tweets with coordinates."""
    api = Api.get_default()
    if api.channel == Api.OFFICIAL:
        assert api.is_official
        tweets = api.get_tweets_map(where=['-122.75,36.8,-121.75,37.8'], lang=['en'], pages=1)
        assert isinstance(tweets, types.GeneratorType)
        tweet = next(tweets)  # generatre some tweets
        assert isinstance(tweet, dict)  # check if tweets are readable
        assert 'tweet' in tweet
        assert 'coordinates' in tweet['geometry']
