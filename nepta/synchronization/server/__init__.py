import json
from logging import info, debug

try:
    from xmlrpc.server import SimpleXMLRPCServer
except ImportError:
    # this is compatible fix for python 2 and 3
    from SimpleXMLRPCServer import SimpleXMLRPCServer


class HostJobState(object):
    def __init__(self, host, job, state):
        self._host = host
        self._job = job
        self._state = state

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def job(self):
        return self._job

    @job.setter
    def job(self, job):
        self._job = job

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def __str__(self):
        return 'HostTestState: %s %s %s' % (self._host, self._job, self._state)


class HostTestStore(list):
    pass


class PersistentTestStore(object):

    def __init__(self, file_name='sync_state.json'):
        self._file_name = file_name
        self._hosts = {}

    def __getitem__(self, key):
        return self._hosts[key]

    def __setitem__(self, key, value):
        self._hosts[key] = value
        value.store = self

    def save(self):
        context = {}
        for host, state in self._hosts.items():
            context[state.host] = {'job': state.job, 'state': state.state}
        with open(self._file_name, 'w') as f:
            json.dump(context, f)

    def load(self):
        self._hosts = {}
        with open(self._file_name, 'r') as f:
            store = json.load(f)
            for host, state in store.items():
                self._hosts[host] = HostJobState(host=host, job=state['job'])
                self._hosts[host].set_state(state['state'])


class SyncServer(object):

    def __init__(self, store):
        self._store = store

    def set_state(self, host, job, state):
        info("SyncServer, setting state: host=%s, job=%s, state=%s", host, job, state)
        try:
            old_job = self._store[host].job
            old_state = self._store[host].state
            self._store[host].job = job
            self._store[host].state = state
            info('SyncServer, updating state: host=%s, old_job=%s, new_job=%s, old_state=%s, new_state=%s', host,
                  old_job, job, old_state, state)
        except KeyError:
            debug('SyncServer, creating state: host=%s, job=%s, state=%s', host, job, state)
            self._store[host] = HostJobState(host, job, state)
        self._store.save()

    def get_state(self, host):
        try:
            item = self._store[host]
            info('SyncServer, returning state: host=%s, job=%s, state=%s', host, item.job, item.state)
            return item.job, item.state
        except KeyError:
            info('SyncServer, state not found host: %s', host)
            return None, None


class ServerCreator(object):

    @classmethod
    def create(cls, addr='0.0.0.0', port=8000, log=False):
        store = PersistentTestStore()
        instance = SyncServer(store)
        xrpc_server = SimpleXMLRPCServer((addr, port), allow_none=True, logRequests=log)
        xrpc_server.register_instance(instance)
        return xrpc_server
