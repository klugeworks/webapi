class Config(object):
    DEBUG = False
    TESTING = False
    KLUGE_WEB_DATASTORE = 'TodoDAO'


class ProductionConfig(Config):
    KLUGE_WEB_DATASTORE = 'TodoDAO2'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True