import socket
import time
from logging import warning, debug, info

try:
    import xmlrpc.client as xmlrpc_client
except ImportError:
    import xmlrpclib as xmlrpc_client


class ServerUnavailabe(Exception):
    pass


class ToleranceNotAvailable(Exception):
    pass


def fault_tolerant(method):

    def inner(instance, *args, **kwargs):
        if not hasattr(instance,'count') or not hasattr(instance,'timeout'):
            raise ToleranceNotAvailable
        err_no = 0
        cont = True
        while cont:
            try:
                not err_no or time.sleep(instance.timeout)
                ret = method(instance, *args, **kwargs)
                break
            except ConnectionError:
                warning("Connection refused during %s", method.__name__)
                err_no += 1
            cont = err_no < instance.count
        else:
            raise ServerUnavailabe
        return ret
    return inner


class SyncClient(object):

    def __init__(self, server, port=8000, timeout=10, count=720):
        self.hostname = socket.gethostname()
        self.port = port
        self.timeout = timeout
        self.count = count
        self.proxy = xmlrpc_client.ServerProxy("http://%s:%s/" % (server, port))

    @fault_tolerant
    def set_state(self, job, state):
        debug('SyncClient, setting state host=%s, job=%s, state=%s', self.hostname, job, state)
        self.proxy.set_state(self.hostname, job, state)

    @fault_tolerant
    def get_state(self, other_hostname):
        debug('SyncClient, getting state host:%s', other_hostname)
        job, state = self.proxy.get_state(other_hostname)
        info('SyncClient state of host:%s job:%s is %s', other_hostname, job, state)
        return job, state

    def wait_for_state(self, other_hostname, job, state, poll=20):
        debug('SyncClient, waiting for host=%s, job=%s, state=%s', other_hostname, job, state)
        current_job, current_state = self.get_state(other_hostname)

        while current_state not in state or current_job != job:
            current_job, current_state = self.get_state(other_hostname)
            time.sleep(poll)

        return current_state
