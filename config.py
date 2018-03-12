"""
Class pattern for configuration
"""


class Config(object):
    DEBUG = False
    TESTING = False

    # twitter credentials
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
