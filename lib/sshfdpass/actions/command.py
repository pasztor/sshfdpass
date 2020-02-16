import os
import socket
import sshfdpass.actions
import sshfdpass.common
from sshfdpass.common.exceptions import *

log = sshfdpass.common.log

class Action(sshfdpass.actions.AbstractAction):
    def _execute(self, host, port, actionarg=None, kwargs={}):
        # If we don't have an actual actionarg, than we have to get my parameters
        # via the "default" method
        if actionarg is None:
            command = self._get('command', kwargs)
            myargs = self._get('args', kwargs)
            arglist = [ command ]
        # If we have a list as an actionarg, than that's my command and arguments
        elif isinstance(actionarg, list):
            if len(actionarg) > 0:
                command = actionarg[0]
                arglist = [ command ]
                myargs = list(actionarg)
                del(myargs[0])
            else:
                raise(sshfdpassException)
        # We won't deal with any other type of actionarg
        else:
            raise(sshfdpassException)
        # We have to parse every arg, to replace %h and %p strings to host and port
        argparserules = {
                'h': self._get('host', kwargs, host),
                'p': str(self._get('port', kwargs, port)) }
        for arg in myargs:
            arglist.append(sshfdpass.common.argparse(arg,argparserules))
        # Just for debug reasons, log the actual command whaw we would run
        log.message('command action called: %s(%s)'%(command, arglist))
        # Since we have to pass back a socket's fd, we have to fork that child and bound it's stdin/out/err to ourself
        mysockpair = socket.socketpair()
        childpid = os.fork()
        # If I'm the parent, then I have to close the other half of the socket pair, and give back my half to the caller ssh process
        if childpid:
            mysockpair[1].close()
            return mysockpair[0]
        # If I'm the child, then I should close the parent's socketpair half, and dup my half to stdin/out/err
        # Then I can do my exec()
        else:
            mysockpair[0].close()
            mysock = mysockpair[1]
            os.dup2(mysock.fileno(), 0)
            os.dup2(mysock.fileno(), 1)
            os.dup2(mysock.fileno(), 2)
            os.execvp(command, arglist)
        return None
