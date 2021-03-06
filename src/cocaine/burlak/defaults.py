from .logger import ConsoleLogger


class Defaults(object):
    '''App-wide defaults
    '''
    TOK_UPDATE_SEC = 10

    WEB_PORT = 8877
    WEB_PATH = ''

    # TODO: make mandatory and config only
    UUID_PATH = '/darkvoice/states'

    FEEDBACK_PATH = '/darkvoice/feedback'
    DISCOVERY_PATH = '/darkvoice/discovery'

    DISCOVERY_UPDATE_INTERVAL_SEC = 3600

    METRICS_PATH = '/darkvoice/metrics'
    METRICS_POLL_INTERVAL_SEC = 5

    NODE_SERVICE_NAME = 'node'
    UNICORN_SERVICE_NAME = 'unicorn'

    PROFILE_NAME = 'default'

    LOCATOR_HOST = 'localhost'
    LOCATOR_PORT = 10053

    STOP_APPS_NOT_IN_STATE = False
    PENDING_STOP_IN_STATE = False

    SENTRY_DSN = ''

    EXPIRE_STOPPED_SEC = 900

    # Default is skip all console logging.
    CONSOLE_LOGGER_LEVEL = int(ConsoleLogger.ERROR) + 1

    STATUS_WEB_PATH = r'/status'
    STATUS_PORT = 9878

    APPS_POLL_INTERVAL_SEC = 60
    INPUT_QUEUE_SIZE = 1024

    STOP_BY_CONTROL = True
    CONTROL_WITH_ACK = False

    APPLY_CONTROL = False
    FILTER_PATH = '/darkvoice/control_filter'

    API_TIMEOUT = 300

    ON_AYNC_ERROR_TIMEOUT_SEC = 10

    SHARDING_ENABLED = False
    FALLBACK_SHARDING_TAG = '_unspec'
    SHARDING_COMMON_PREFIX = '/darkvoice/sharding'

    DC_TAG_KEY = 'x-cocaine-cluster'

    SHARDING_FEEDBACK_SUBNODE = 'feedback'
    SHARDING_STATE_SUBNODE = 'state'
    SHARDING_METRICS_SUBNODE = 'metrics'
