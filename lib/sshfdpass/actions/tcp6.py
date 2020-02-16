import sshfdpass.actions.tcp

class Action(sshfdpass.actions.tcp.Action):
    def _defaults(self):
        return dict(aforder='6')
