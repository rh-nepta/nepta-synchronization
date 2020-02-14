import logging
import sys
import signal

import argparse
from nepta.synchronization import server

DEFAULT_LOGGING_MODE = 'INFO'

logger = logging.getLogger(__name__)


def exitf(a, b):
    logger.info('Exitting on user request')
    sys.exit()


def main():
    parser = argparse.ArgumentParser(description='Server tool for multi-host test synchronization')
    parser.add_argument('--address', action='store', default='0.0.0.0', help='Server listening address [Default: %(default)s]')
    parser.add_argument('--port', type=int, action='store', default=8000, help='Server listening port [Default: %(default)s]')
    parser.add_argument('--store', type=str, action='store', default='/var/run/nepta-synchronization/sync-state.json',
                        help='persistent state storage path')

    parser.add_argument('-l', '--log', action='store', type=str.upper, choices=['DEBUG', 'WARNING', 'INFO', 'ERROR', 'EXCEPTION'], default=DEFAULT_LOGGING_MODE, help='Logging level [Default: %(default)s]')

    args = parser.parse_args()
    logging.basicConfig(level=args.log)

    signal.signal(signal.SIGINT, exitf)
    logger.info('Starting synchronization server at %s:%s', args.address, args.port)

    s = server.ServerCreator.create(addr=args.address, port=args.port, store_path=args.store)
    s.serve_forever()


if __name__ == '__main__':
    main()
