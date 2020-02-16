#

'''
sshfdpass.actions
-----------------

This package provides an Abstract base class to build actions upon.
The abstraction in the nutshell: action got the settings from the instance
and host, port, runtime args and kwargs as execution parameters.
At the and of the rule evaluation, and an action will be execute() -ed.
Worst case scenario the default action will got the control, which is the tcp.
In general, if there would no proxycommand and proxypassfd options defined in
the ssh's config file, it would connect to the given host and port via tcp.
So the fallback tcp action does transparently the same:
If no written rule were matched, act like otherwise.

Like tests can have settings and target, actions can get settings.
If a setting should be different than the test default settings, it can
still be overriden on a per rule basis.
Eg. you want to define a shortcut to a host which don't have dns entry, you
can do the following rule:
    rules:
        hostname:
            - action: tcp
              tcp.host: 1.2.3.4

This way, if you try to run the ssh hostname command, it will connect to 1.2.3.4 underneath.
The thumbrule with rule evaluation:
A rule is a dict. It must have an `action` key. Let's say it's tcp.
If you want to give a local setting for the tcp action on this particular rule's execution,
than tcp.* keys will be passed to the action, but with the removed prefixes.
This way, tcp will get the host key as a kwarg parameter and that host will override the
always present host coming from the caller ssh process.

This module provides an AbstractAction class.
All the action classes must based on this class.
The most important method what a child class must override is the _execute().
The _execute() should return an object which has a fileno() method.
Therefore an opened tcp socket, or unix socket, or any kind of socket will do the job.
The point is, that the parent class should be able to get its' fileno and pass it to the caller ssh process.
'''

import socket
import array
import sshfdpass.common
from sshfdpass.common.exceptions import *

log = sshfdpass.common.log

class AbstractAction():
    def __init__(self, **kwargs):
        self.settings=self._defaults()
        self.settings.update(kwargs)

    def _defaults(self):
        return dict()

    def _keywords(self):
        return []

    def _get(self, name, kwargs={}, default=None):
        return kwargs.get(name, self.settings.get(name, default))

    def _execute(self, host, port, actionarg=None, kwargs={}):
        return None

    def execute(self, host, port, actionarg=None, kwargs={}):
        log.message('executing action %s (%s, %s, %s, %s)'%(type(self), host, port, actionarg, kwargs))
        # We have to calculate the actual kwargs, and overwrite some of them
        # If we have defined keywords and actionarg is a dict, containing any key which is one of our keywords
        callkwargs = dict()
        callkwargs.update(kwargs)
        if isinstance(actionarg, dict):
            for i in actionarg:
                if i in self._keywords():
                    callkwargs[i] = actionarg[i]
        # Now we can call the actual execution safely
        retsocket = self._execute(
                self._get('host', kwargs, host),
                int(self._get('port', kwargs, port)),
                actionarg,
                callkwargs
                )
        try:
            fileno = retsocket.fileno()
        except AttributeError as exc:
            raise(sshfdpassActionError)
        # If we got to this point, that means, the descendant class did it's job, we can pass back the fd to the caller
        fds = array.array("i", [fileno])
        try:
            scm = socket.SCM_RIGHTS
        except AttributeError: # python2 compatibility
            scm = 1
        ancdata = [(socket.SOL_SOCKET, scm, fds)]
        try:
            s = socket.socket( fileno = 1)
        except TypeError: # py2 compat hack
            s = socket.fromfd( 1, socket.AF_UNIX, socket.SOCK_STREAM)
        s.sendmsg([b'\0'], ancdata)
        return True
