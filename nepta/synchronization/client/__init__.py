import socket
import time
from logging import warning, debug, info

try:
    import xmlrpc.client as xmlrpc_client
except ImportError:
    import xmlrpclib as xmlrpc_client


class ServerUnavailabe(Exception):
    pass


class SyncClient(object):

    def __init__(self, server, port=8000):
        self.hostname = socket.gethostname()
        self.port = port
        self.proxy = xmlrpc_client.ServerProxy("http://%s:%s/" % (server, port))
        self._err_no = 0
        self._err_retry = 5
        self._allowed_errs = 3

    def set_state(self, job, state):
        debug('SyncClient, setting state host=%s, job=%s, state=%s', self.hostname, job, state)
        self.proxy.set_state(self.hostname, job, state)

    def get_state(self, other_hostname):
        debug('SyncClient, getting state host:%s', other_hostname)
        while self._err_no < self._allowed_errs:
            try:
                job, state = self.proxy.get_state(other_hostname)
                info('SyncClient state of host:%s job:%s is %s', other_hostname, job, state)
                break
            except ConnectionRefusedError:
                warning('SyncClient connection to %s:%s refused' % (self.hostname, self.port))
                self._err_no += 1
                time.sleep(self._err_retry)
        else:
            raise ServerUnavailabe

        return job, state

    def wait_for_state(self, other_hostname, job, state, poll=20):
        debug('SyncClient, waiting for host=%s, job=%s, state=%s', other_hostname, job, state)
        current_job, current_state = self.get_state(other_hostname)

        while current_state not in state or current_job != job:
            current_job, current_state = self.get_state(other_hostname)
            time.sleep(poll)

        return current_state
