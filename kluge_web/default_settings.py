class Config(object):
    DEBUG = False
    TESTING = False
    KLUGE_WEB_DATASTORE = 'KlugeRedis'
    #KLUGE_DS_HOSTNAME = 'redis.marathon.mesos'
    KLUGE_DS_HOSTNAME = '10.30.3.24'
    KLUGE_DS_PORT = 6379


class ProductionConfig(Config):
    KLUGE_WEB_DATASTORE = 'KlugeRedis'
    #KLUGE_DS_HOSTNAME = 'redis.marathon.mesos'
    KLUGE_DS_HOSTNAME = '10.30.3.24'
    KLUGE_DS_PORT = 6379


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True