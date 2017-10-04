#
# TODO:
#
# DONE:
#   - endpoints for logger
#
import burlak

import click

from cocaine.logger import Logger
# TODO: not released yet!
# from cocaine.services import SecureServiceFabric, Service
from cocaine.services import Service

from tornado import queues
from tornado.ioloop import IOLoop

from .comm_state import CommittedState
from .config import Config
from .context import Context, LoggerSetup
from .helpers import SecureServiceFabric
from .sentry import SentryClientWrapper
from .uniresis import catchup_an_uniresis
from .web import Uptime, make_web_app

try:
    from .ver import __version__
    __version__ = str(__version__)
except ImportError:
    __version__ = 'unknown'


# TODO: get from config!
APP_LIST_POLL_INTERVAL = 15


@click.command()
@click.option(
    '--uuid-prefix', help='state prefix (unicorn path)')
@click.option(
    '--apps-poll-interval',
    default=APP_LIST_POLL_INTERVAL, help='default profile for app running')
@click.option('--port', type=int, help='web iface port')
@click.option(
    '--uniresis-stub-uuid', help='use uniresis stub with provided uuid')
@click.option(
    '--dup-to-console',
    is_flag=True, default=False, help='copy logger output to console')
@click.option(
    '--console-log-level',
    # CocaineError.ERROR (max level) + 1 means disabled
    # See CocaineError.LEVELS for valid lavels numbers
    default=Config.DEFAULT_CONSOLE_LOGGER_LEVEL,
    help='if console logger is active, setup loglevel'
)
def main(
        uuid_prefix,
        apps_poll_interval,
        port,
        uniresis_stub_uuid,
        dup_to_console,
        console_log_level):

    config = Config()
    config.update()

    config.console_log_level = console_log_level

    input_queue, control_queue, sync_queue = \
        (queues.Queue() for _ in xrange(3))
    logger = Logger(config.locator_endpoints)

    unicorn = SecureServiceFabric.make_secure_adaptor(
        Service(config.unicorn_name, config.locator_endpoints),
        *config.secure, endpoints=config.locator_endpoints)

    node = Service(config.node_name, config.locator_endpoints)
    node_ctl = Service(config.node_name, config.locator_endpoints)

    uniresis = catchup_an_uniresis(
        uniresis_stub_uuid, config.locator_endpoints)

    sentry_wrapper = SentryClientWrapper(
        logger, dsn=config.sentry_dsn, revision=__version__)

    context = Context(
        LoggerSetup(logger, dup_to_console),
        config,
        __version__,
        sentry_wrapper)

    committed_state = CommittedState()

    acquirer = burlak.StateAcquirer(context, input_queue)
    state_processor = burlak.StateAggregator(
        context,
        node,
        committed_state,
        input_queue, control_queue, sync_queue,
        apps_poll_interval)

    apps_elysium = burlak.AppsElysium(
        context, committed_state,
        node, node_ctl,
        control_queue, sync_queue)

    if not uuid_prefix:
        uuid_prefix = config.uuid_path

    # run async poll tasks in date flow reverse order, from sink to source
    io_loop = IOLoop.current()
    io_loop.spawn_callback(apps_elysium.blessing_road)
    io_loop.spawn_callback(state_processor.process_loop)

    # io_loop.spawn_callback(
    #     # TODO: make node list constructor parameter
    #     lambda: acquirer.poll_running_apps_list(node_list))
    io_loop.spawn_callback(
        lambda: acquirer.subscribe_to_state_updates(
            unicorn, node, uniresis, uuid_prefix))

    qs = dict(input=input_queue, control=control_queue, sync=sync_queue)
    units = dict(
        state_acquisition=acquirer,
        state_dispatch=state_processor,
        elysium=apps_elysium)

    cfg_port, prefix = config.web_endpoint

    if not port:
        port = cfg_port

    # TODO: use non-default address
    uptime = Uptime()
    app = make_web_app(
        prefix, uptime, uniresis, committed_state, qs, units, __version__)
    app.listen(port)

    click.secho('orca is starting...', fg='green')
    IOLoop.current().start()


if __name__ == '__main__':
    main()
