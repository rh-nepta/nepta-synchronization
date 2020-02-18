import logging
import sys
import argparse

from nepta.synchronization import client

DEFAULT_LOGGING_MODE = 'WARNING'
DEFAULT_SYNC_SERVER = '0.0.0.0'

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Client tool for multi-host test synchronization')
    parser.add_argument('--server', type=str, action='store', default=DEFAULT_SYNC_SERVER, help='Server hostname [Default: %(default)s]')
    parser.add_argument('--port', type=int, action='store', default=client.SyncClient.DEFAULT_PORT, help='Server port [Default: %(default)s]')

    parser.add_argument('--job', action='store', required=True, help='Beaker job ID')
    parser.add_argument('--set', nargs='?', action='store', help='Set state')
    parser.add_argument('--wait', nargs=2, action='append', metavar=('host', 'states',), help='Wait for host state')

    parser.add_argument('--count', type=int, nargs='?', action='store', default=client.SyncClient.NUMBER_OF_CONN_RETRIES,
                        help='Count of unsuccesfull attempts before bailing out [Default: %(default)s]')
    parser.add_argument('--timeout', type=int, nargs='?', action='store', default=client.SyncClient.DEFAULT_CONNECTION_TIMEOUT,
                        help='Wait in second before next try when server is unavailable [Default: %(default)s]')

    parser.add_argument('-l', '--log', action='store', type=str.upper, choices=['DEBUG', 'WARNING', 'INFO', 'ERROR', 'EXCEPTION'], default=DEFAULT_LOGGING_MODE, help='Logging level [Default: %(default)s]')

    args = parser.parse_args()

    # Setup script logging
    logging.basicConfig(level=args.log)

    if args.set is None and args.wait is None:
        logger.error('No operation specified, exiting.')
        # this return code is special for informing executor about no operation specified
        sys.exit(42)

    logger.info('Starting synchronization client. Using synchronization server at %s:%s', args.server, args.port)

    c = client.SyncClient(
        server=args.server,
        port=args.port,
        timeout=args.timeout,
        count=args.count,
    )

    if args.set:
        logger.info('Setting own state: test=%s state=%s', args.job, args.set)
        c.set_state(args.job, args.set)

    if args.wait:
        for sync_host, sync_states in args.wait:
            sync_state_list = sync_states.split(',')
            logger.info('Waiting for other host: host=%s, job=%s, state=%s', sync_host, args.job, sync_state_list)
            c.wait_for_state(sync_host, args.job, sync_state_list)


if __name__ == '__main__':
    main()
