from logging import info, debug

try:
    from xmlrpc.server import SimpleXMLRPCServer
except ImportError:
    # this is compatible fix for python 2 and 3
    from SimpleXMLRPCServer import SimpleXMLRPCServer


class HostJobState(object):
    def __init__(self, host, job):
        self._host = host
        self._job = job
        self._state = None

    def get_host(self):
        return self._host

    def set_job(self, job):
        self._job = job

    def get_job(self):
        return self._job

    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self._state

    def __str__(self):
        return 'HostTestState: %s %s %s' % (self._host, self._job, self._state)


class HostTestStore(list):
    pass


class SyncServer(object):

    def __init__(self, store):
        self._store = store

    def set_state(self, host, job, state):
        info("SyncServer, setting state: host=%s, job=%s, state=%s", host, job, state)
        state_updated = False
        for item in self._store:
            if item.get_host() == host:
                old_job = item.get_job()
                debug('SyncServer, updating state: host=%s, old_job=%s, new_job=%s, old_state=%s, new_state=%s', host, old_job, job, item.get_state(), state)
                item.set_state(state)
                item.set_job(job)
                state_updated = True

        if not state_updated:
            debug('SyncServer, creating state: host=%s, job=%s, state=%s', host, job, state)
            new = HostJobState(host, job)
            new.set_state(state)
            self._store.append(new)
            state_updated = True

    def get_state(self, host):
        debug("SyncServer, getting state of %s", host)
        for item in self._store:
            debug("%s == %s" % (host, item.get_host()))
            if item.get_host() == host:
                state = item.get_state()
                job = item.get_job()
                debug('SyncServer, returning state: host=%s, job=%s, state=%s', host, job, state)
                return job, state

        debug('SyncServer, state not found host: %s', host)
        return None, None


class ServerCreator(object):

    @classmethod
    def create(cls, addr='0.0.0.0', port=8000, log=False):
        store = HostTestStore()
        instance = SyncServer(store)
        xrpc_server = SimpleXMLRPCServer((addr, port), allow_none=True, logRequests=log)
        xrpc_server.register_instance(instance)
        return xrpc_server
