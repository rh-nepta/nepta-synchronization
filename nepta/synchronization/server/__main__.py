import logging
from logging import info
import sys
import signal

import argparse
from nepta.synchronization import server

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_LOGGING_MODE = 'WARNING'


def exitf(a, b):
    info('Exitting on user request')
    sys.exit()


def main():
    parser = argparse.ArgumentParser(description='Server tool for multi-host test synchronization')
    parser.add_argument('--address', action='store', default='0.0.0.0', help='Server listening address [Default: %(default)s]')
    parser.add_argument('--port', type=int, action='store', default=8000, help='Server listening port [Default: %(default)s]')
    parser.add_argument('-l', '--log', action='store', type=str.upper, choices=['DEBUG', 'WARNING', 'INFO', 'ERROR', 'EXCEPTION'], default=DEFAULT_LOGGING_MODE, help='Logging level [Default: %(default)s]')

    args = parser.parse_args()
    logging.basicConfig(level=args.log)

    signal.signal(signal.SIGINT, exitf)
    info('Starting synchronization server at %s:%s', args.address, args.port)

    s = server.ServerCreator.create(args.address, args.port)
    s.serve_forever()


if __name__ == '__main__':
    main()
