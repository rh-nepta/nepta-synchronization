import logging
from logging import info
import sys
import signal

import argparse
from nepta.synchronization import server

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def exitf(a, b):
    info('Exitting on user request')
    sys.exit()


def main():
    parser = argparse.ArgumentParser(description='Server tool for multi-host test synchronization')
    parser.add_argument('--address', action='store', default='0.0.0.0', help='Server listening address [Default: %(default)s]')
    parser.add_argument('--port', type=int, action='store', default=8000, help='Server listening port [Default: %(default)s]')

    signal.signal(signal.SIGINT, exitf)
    args = parser.parse_args()
    info('Starting synchronization server at %s:%s', args.address, args.port)

    s = server.ServerCreator.create(args.address, args.port)
    s.serve_forever()


if __name__ == '__main__':
    main()
