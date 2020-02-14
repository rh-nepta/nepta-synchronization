import json
from logging import info, debug
from xmlrpc.server import SimpleXMLRPCServer


class HostJobState:

    guarded_property = {
        'host': '_host',
        'job': '_job',
        'state': '_state',
        'store': '_store',
    }

    def __init__(self, host, job, state):
        self.foo = 'foo'
        self._host = host
        self._job = job
        self._state = state
        self._store = None

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            guarded_name = self.guarded_property[name]
            return object.__getattribute__(self, guarded_name)

    def __setattr__(self, name, value):
        try:
            guarded_name = self.guarded_property[name]
            object.__setattr__(self, guarded_name, value)
            if self._store is not None:
                self._store.save()
        except KeyError:
            object.__setattr__(self, name, value)

    def __str__(self):
        return 'HostTestState host:%s job:%s state:%s' %\
               (self._host, self._job, self._state)


class PersistentTestStore:

    def __init__(self, file_name='sync_state.json'):
        self._file_name = file_name
        self._hosts = {}
        self.load()

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
        try:
            with open(self._file_name, 'r') as f:
                store = json.load(f)
                for host, state in store.items():
                    s = HostJobState(host=host, job=state['job'], state=state['state'])
                    self[host] = s
                    debug('loading state %s' % s)
        except FileNotFoundError:
            info("Persistent file %s not found" % self._file_name)


class SyncServer:

    def __init__(self, store):
        self._store = store

    def set_state(self, host, job, state):
        debug("Setting state: host %s, job %s, state %s", host, job, state)
        try:
            old_job = self._store[host].job
            old_state = self._store[host].state
            self._store[host].job = job
            self._store[host].state = state
            debug('SyncServer, updating state: host %s, job %s -> %s, state=%s -> %s', host,
                  old_job, job, old_state, state)
        except KeyError:
            debug('SyncServer, creating state: host %s, job %s, state %s', host, job, state)
            self._store[host] = HostJobState(host, job, state)

    def get_state(self, host):
        try:
            item = self._store[host]
            debug('Returning state: host %s, job %s, state %s', host, item.job, item.state)
            return item.job, item.state
        except KeyError:
            debug('State not found host: %s', host)
            return None, None


class ServerCreator:

    @classmethod
    def create(cls, addr='0.0.0.0', port=8000, log=False):
        store = PersistentTestStore()
        instance = SyncServer(store)
        xrpc_server = SimpleXMLRPCServer((addr, port), allow_none=True, logRequests=log)
        xrpc_server.register_instance(instance)
        return xrpc_server
