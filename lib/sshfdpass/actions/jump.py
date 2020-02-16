import sshfdpass.common
from sshfdpass.common.exceptions import *
from sshfdpass.actions import command

log = sshfdpass.common.log

class Action(command.Action):
    def _execute(self, host, port, actionarg=None, kwargs={}):
        log.message('jump called: host: %s, port: %s, actionarg: %s, kwargs: %s'%(host, port, actionarg, kwargs))
        if isinstance(actionarg, str):
            _actionarg = [ actionarg ]
        else:
            _actionarg = actionarg
        args = [ 'ssh', '-W', '[%s]:%s'%(
            self._get('host', kwargs, host),
            str(self._get('port', kwargs, port))) ]
        jumphost = _actionarg[-1:][0]
        if len(_actionarg) > 1:
            args.append('-J')
            args.append(','.join(_actionarg[:-1]))
        args.append(jumphost)
        log.message('calling parent class with args: host: %s, port: %s, actionarg: %s, kwargs: %s'%(host, port, args, kwargs))
        # TODO: tried to make it py2 compatible. Still not working.
        return super(type(self), self)._execute(host, port, args, kwargs)
