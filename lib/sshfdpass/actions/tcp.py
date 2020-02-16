import socket
import sshfdpass.actions
from sshfdpass.common.exceptions import *

class Action(sshfdpass.actions.AbstractAction):
    def _defaults(self):
        return dict(aforder='6,4')

    def _execute(self, host, port, actionargs=None, kwargs={}):
        aflist = self.settings.get('aforder').split(',')
        for af in aflist:
            if af == '4':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            elif af == '6':
                s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
            else:
                raise(sshfdpassAFUnkown)
            try:
                s.connect((host, port))
            except socket.gaierror as exc:
                continue
            return s
        return None
