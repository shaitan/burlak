from cocaine.burlak import Config

import pytest

DEFAULT_UPDATE_SEC = Config.DEFAULT_TOK_UPDATE_SEC

good_secret_conf = [
    ('tests/assets/conf1.yaml',
        'BOO_MOD', 100500, 'top secret', DEFAULT_UPDATE_SEC),
    ('tests/assets/conf2.yaml',
        'Classified', 42, 'not as secret at all', 600),
]

broken_conf = 'tests/assets/broken.conf.yaml'


@pytest.mark.parametrize(
    'config_file,mod,cid,secret,update', good_secret_conf)
def test_secure_config(config_file, mod, cid, secret, update):
    cfg = Config()
    cnt = cfg.update([config_file])

    assert cfg.secure == \
        (mod, cid, secret, update)
    assert cnt == 1


def test_config_group():
    cfg = Config()
    cnt = cfg.update([conf for conf, _, _, _, _ in good_secret_conf])

    assert cfg.secure == (good_secret_conf[-1][1:])
    assert cnt == len(good_secret_conf)


def test_broken_conf():
    cfg = Config()
    cnt = cfg.update([broken_conf])

    assert cnt == 0


def test_config_group_with_broken():
    conf_files = [conf for conf, _, _, _, _ in good_secret_conf]
    conf_files.append(broken_conf)

    print(conf_files)

    cfg = Config()
    cnt = cfg.update(conf_files)

    assert cfg.secure == (good_secret_conf[-1][1:])
    assert cnt == len(good_secret_conf)


def test_config_group_with_broken_and_noexist():
    conf_files = [broken_conf, 'boo/foo.yml']

    cfg = Config()
    cnt = cfg.update(conf_files)

    assert cnt == 0
    assert cfg.secure == ('promisc', 0, '', DEFAULT_UPDATE_SEC)
