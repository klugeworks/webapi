class Config(object):
    DEBUG = False
    TESTING = False
    KLUGE_WEB_DATASTORE = 'KlugeRedis'
    KLUGE_DS_HOSTNAME = 'redis.marathon.mesos'
    KLUGE_DS_PORT = 6379
    KLUGE_STATSD_HOSTNAME = 'statsd.stats.marathon.mesos'
    KLUGE_STATSD_PORT = 31990


class ProductionConfig(Config):
    KLUGE_WEB_DATASTORE = 'KlugeRedis'
    KLUGE_DS_HOSTNAME = 'redis.marathon.mesos'
    KLUGE_DS_PORT = 6379
    KLUGE_STATSD_HOSTNAME = 'statsd.stats.marathon.mesos'
    KLUGE_STATSD_PORT = 31990


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True