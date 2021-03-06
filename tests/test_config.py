from cocaine.burlak import Config, ConsoleLogger
from cocaine.burlak.control_filter import ControlFilter
from cocaine.burlak.defaults import Defaults
from cocaine.burlak.mokak.mokak import SharedStatus

import pytest


good_secret_conf = [
    ('tests/assets/conf1.yaml',
        'test1', 100500, 'top secret', Defaults.TOK_UPDATE_SEC),
    ('tests/assets/conf2.yaml',
        'tvm', 42, 'not as secret at all', 600),
]

empty_conf = 'tests/assets/empty.conf.yaml'

default_secure = ('promisc', 0, '', Defaults.TOK_UPDATE_SEC)

shared_status = SharedStatus()


@pytest.mark.parametrize(
    'config_file,mod,cid,secret,update', good_secret_conf)
def test_secure_config(config_file, mod, cid, secret, update):
    cfg = Config(shared_status)
    cnt = cfg.update([config_file])

    assert cfg.secure == (mod, cid, secret, update)
    assert cnt == 1


def test_config_group():
    cfg = Config(shared_status)
    cnt = cfg.update([conf for conf, _, _, _, _ in good_secret_conf])

    assert cfg.secure == (good_secret_conf[-1][1:])
    assert cnt == len(good_secret_conf)


def test_broken_conf():
    cfg = Config(shared_status)
    cnt = cfg.update([empty_conf])

    assert cnt == 1


def test_config_group_with_broken():
    conf_files = [conf for conf, _, _, _, _ in good_secret_conf]
    conf_files.append(empty_conf)

    cfg = Config(shared_status)
    cnt = cfg.update(conf_files)

    assert cfg.secure == (good_secret_conf[-1][1:])
    assert cnt == len(good_secret_conf) + 1


def test_config_group_with_broken_and_noexist():
    conf_files = [empty_conf, 'boo/foo.yml']

    cfg = Config(shared_status)
    cnt = cfg.update(conf_files)

    assert cnt == 1
    assert cfg.secure == default_secure


def test_empty_config():
    cfg = Config(shared_status)
    assert cfg.secure == default_secure


@pytest.mark.parametrize(
    'config,expect_port,expect_web_path,expect_uuid_path',
    [
        ('tests/assets/conf1.yaml', 100500, '', Defaults.UUID_PATH),
        ('tests/assets/conf2.yaml', 8877, '/to-heaven', '/some/deep/location'),
    ]
)
def test_endpoints_options(
        config, expect_port, expect_web_path, expect_uuid_path):

    cfg = Config(shared_status)
    cfg.update([config])

    assert (expect_port, expect_web_path) == cfg.web_endpoint
    assert expect_uuid_path == cfg.uuid_path


@pytest.mark.parametrize(
    'config,expect_unicorn_name,expect_node_name',
    [
        ('tests/assets/conf1.yaml', 'unicorn', 'some_other_node'),
        ('tests/assets/conf2.yaml', 'big_unicorn', 'node'),
    ]
)
def test_service_names(config, expect_unicorn_name, expect_node_name):
    cfg = Config(shared_status)
    cfg.update([config])

    assert expect_unicorn_name == cfg.unicorn_name
    assert expect_node_name == cfg.node_name


@pytest.mark.parametrize(
    'config,expect_profile,expect_stop_apps,'
    'expect_expire_stopped,expect_log_level',
    [
        (
            'tests/assets/conf1.yaml', 'default', False,
            Defaults.EXPIRE_STOPPED_SEC, 100
        ),
        (
            'tests/assets/conf2.yaml',
            'isolate_profile',
            True,
            42,
            int(ConsoleLogger.ERROR) + 1
        ),
    ]
)
def test_misc_options(
        config,
        expect_profile, expect_stop_apps,
        expect_expire_stopped, expect_log_level):

    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.default_profile == expect_profile
    assert cfg.stop_apps == expect_stop_apps
    assert cfg.expire_stopped == expect_expire_stopped
    assert cfg.console_log_level == expect_log_level


@pytest.mark.parametrize(
    'config,status_web_path,status_port',
    [
        ('tests/assets/conf1.yaml', r'/status', 10042),
        ('tests/assets/conf2.yaml', r'/boo', 9878),
    ]
)
def test_extra1(config, status_web_path, status_port):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.status_web_path == status_web_path
    assert cfg.status_port == status_port


@pytest.mark.parametrize(
    'config,apps_poll_interval_sec,input_queue_size',
    [
        ('tests/assets/conf1.yaml', 100500, 1024),
        ('tests/assets/conf2.yaml', Defaults.APPS_POLL_INTERVAL_SEC, 42),
    ]
)
def test_extra2(config, apps_poll_interval_sec, input_queue_size):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.apps_poll_interval_sec == apps_poll_interval_sec
    assert cfg.input_queue_size == input_queue_size


@pytest.mark.parametrize(
    'config,expect_dsn',
    [
        ('tests/assets/conf1.yaml', ''),
        ('tests/assets/conf2.yaml', 'https://100400@some.sentry.org'),
    ]
)
def test_sentry_dsn(config, expect_dsn):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.sentry_dsn == expect_dsn


@pytest.mark.parametrize(
    'config,expect_loc_endp',
    [
        ('tests/assets/conf1.yaml',
            [[Defaults.LOCATOR_HOST, Defaults.LOCATOR_PORT], ]),
        ('tests/assets/conf2.yaml', [['host1', 100500], ['host2', 42]]),
        ('tests/assets/conf3.yaml', [[Defaults.LOCATOR_HOST, 10042]])
    ]
)
def test_locator_endpoints(config, expect_loc_endp):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.locator_endpoints == expect_loc_endp


def test_console_log_level_setter():
    console_level = 100500

    cfg = Config(shared_status)
    cfg.console_log_level = console_level

    assert cfg.console_log_level == console_level


@pytest.mark.parametrize(
    'config,expected_filter',
    [
        ('tests/assets/conf1.yaml', ControlFilter(True, ['z', '42'])),
        ('tests/assets/conf2.yaml', ControlFilter(False, [])),
        ('tests/assets/conf3.yaml', ControlFilter(False, [])),
    ]
)
def test_control_filter(config, expected_filter):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.control_filter.as_dict() == expected_filter.as_dict()


@pytest.mark.parametrize(
    'expected_filter',
    [
        (ControlFilter(True, ['z', '42'])),
        (ControlFilter(False, [])),
        (ControlFilter(False, [])),
    ]
)
def test_set_control_fitter(expected_filter):
    cfg = Config(shared_status)
    cfg.control_filter = expected_filter
    assert cfg.control_filter.as_dict() == expected_filter.as_dict()


@pytest.mark.parametrize(
    'config,expected_filter_path',
    [
        ('tests/assets/conf1.yaml', 'some/path'),
        ('tests/assets/conf2.yaml', Defaults.FILTER_PATH),
        ('tests/assets/conf3.yaml', 'c:any\weird/string'),
    ]
)
def test_control_filter_path(config, expected_filter_path):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.control_filter_path == expected_filter_path


@pytest.mark.parametrize(
    'config,expected_to',
    [
        ('tests/assets/conf1.yaml', Defaults.API_TIMEOUT),
        ('tests/assets/conf2.yaml', Defaults.API_TIMEOUT),
        ('tests/assets/conf3.yaml', 42),
    ]
)
def test_api_timeout(config, expected_to):
    cfg = Config(shared_status)
    cfg.update([config])

    assert cfg.api_timeout == expected_to
