import socket
import time
import logging
import xmlrpc.client as xmlrpc_client

logger = logging.getLogger(__name__)


class ServerUnavailabe(Exception):
    pass


class ToleranceNotAvailable(Exception):
    pass


def fault_tolerant(method):

    def inner(instance, *args, **kwargs):
        if not hasattr(instance, 'count') or not hasattr(instance, 'timeout'):
            raise ToleranceNotAvailable("'count' or 'timeout' properties of decorated object were not specified!")

        err_no = 0
        cont = True
        while cont:
            try:
                not err_no or time.sleep(instance.timeout)
                ret = method(instance, *args, **kwargs)
                break
            except (ConnectionError, socket.gaierror):
                logger.warning("Connection refused during %s", method.__name__)
                err_no += 1
            cont = err_no < instance.count
        else:
            raise ServerUnavailabe("Max connection retries (%d) were exceeded" % instance.count)
        return ret
    return inner


class SyncClient:

    DEFAULT_PORT = 8000
    DEFAULT_CONNECTION_TIMEOUT = 10
    NUMBER_OF_CONN_RETRIES = 720

    def __init__(self, server, port=DEFAULT_PORT, timeout=DEFAULT_CONNECTION_TIMEOUT, count=NUMBER_OF_CONN_RETRIES):
        self.hostname = socket.gethostname()
        self.port = port
        self.proxy = xmlrpc_client.ServerProxy("http://%s:%s/" % (server, port))

        self.timeout = timeout
        self.count = count

    @fault_tolerant
    def set_state(self, job, state):
        logger.debug('SyncClient, setting state host=%s, job=%s, state=%s', self.hostname, job, state)
        self.proxy.set_state(self.hostname, job, state)

    @fault_tolerant
    def get_state(self, other_hostname):
        logger.debug('SyncClient, getting state host: %s', other_hostname)
        job, state = self.proxy.get_state(other_hostname)
        logger.info('SyncClient state of host=%s, job=%s is %s', other_hostname, job, state)
        return job, state

    def wait_for_state(self, other_hostname, job, state, poll=20):
        logger.debug('SyncClient, waiting for host=%s, job=%s, state=%s', other_hostname, job, state)
        current_job, current_state = self.get_state(other_hostname)

        while current_state not in state or current_job != job:
            current_job, current_state = self.get_state(other_hostname)
            time.sleep(poll)

        time.sleep(poll) # wait for others before next move
        return current_state
