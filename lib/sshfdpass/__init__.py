#

'''
sshfdpass
---------
    A tool to make your ssh configuration more robust.
    Let's say, you have to use different set of jumphosts based on your network location, than this is your tool.

Objectives
----------
    portable for the extremities: I want to deploy this tool to every un*xbox I have. Including older FreeBSD's without extra python modules or pip or anything installed except the base system, which contains a python2.7 interpreter. Therefore I only use the following modules:
    os, sys, pkgutil, socket, array
    yaml/json
    So far, I'm stucked with my poratbility attempts.

Configuration
-------------
Configuration file must be in your home in .ssh/fdpass.conf
Configuration format can be yaml or json.
If yaml python module is provided on the system, it will try to parse the config as yaml.
If there is no yaml around, then it fallbacks to interpret the config file as json.
The content is simple: a dict where the package reads info under the following keys: settings, tests, rules

Settings
--------
    You can set defaults for the tests and actions, therefore the expectation here is a dict again, and this two keys will be considered.
    The value for the tests is another dict, where the key is the name of the test, and the value will be passed to the test on its initialization as kwargs.
    The same applies for the actions.
    Since it's passed as kwargs, expected datatype as a value is a dict again.
    Example for settings:
    tests:
      ipv4range:
        dsthost: 8.8.4.4
        dstport: 53
    actions:
      tcp:
        aforder: 4,6

Tests
-----
    This package already contain one test at this point. TODO: Add more tests
    The one builtin test at the moment is ipv4range.
    By default it tries to connect to 8.8.8.8's port 53, then find out the tcp socket's self address.
    Then you can built your own tests based on this one, like this:
    lan:
      ipv4range:
        - 192.168.0.0/24
    If this is inside your tests, then it will work as the same as the ipv4range test, except it initializes the ipv4range with a predefined list of "target" networks. In this sense target means the target of my ip address check. If my ip address is in the 192.168.0.0/24 range, then the test will evaluate as true.

Rules
-----
    Rule matching is quite simple at the moment. TODO: Improve rule matching, implement wildcard matching
    In the configuration the rules are simple: The key what the rule evaluator looks for in the rules dictionary is the hostname:port pair.
    ssh always calls this helper with %h %p as args. If it was an IP address we get an ip, if that was a hostname, we get an ip.
    We get this from ssh what it was originally. You might setup canonicalization or other overriding rules in your ssh config like this:

    Host somehostname
    HostName someotherhostname

    In this case if you start your ssh as ssh somehostname, than the helper will be called with the "someotherhostname".
    
    After the host:port pair of rules the rules for host will be looked up in the rules dictionary.
    And finally there is a hardcoded default rule: the unconditional tcp action.

    The right hand side of the rules is another dictionary. The rules can have optionally a test key.
    The definition of the test is the same like with the configuration-global tests.
    There is one mandatory field for every rule: The 'action'.
    Action can be: a simple string, like: tcp.
    or a dict, where the dict must have exactly one key, a valid action's name.
    The value belonging to the key will be passed to the action as actionarg, no matter what type does it have.

    example rules:
      hosta:
        - test: lan
          action: tcp4
          tcp4.host: 1.2.3.4
        - action:
            exec:
              - ssh
              - -W
              - '[%h]:%p'
              - 4.3.2.1
      hostb:
        - action: tcp4
          tcp4.host: 4.3.2.1

    This configuration will provide you the following features:
    If you try to `ssh hosta` and you are in the `lan`, then it will directly connect to 1.2.3.4.
    If you are not on your lan, then it will use 4.3.2.1 as a jumphost.
    If you try to ssh to hostb, no matter if that name exists in dns, it will always try to connect to 4.3.2.1

Actions
-------
So far, I could not imagine free form action definition. If you have any idea how it could be useful, don't hesitate to share that with me.
Until that, read all the action's documentation in their own module's page.
Action execution in the rules however can be tricky.

Example
-------
So far, a complete config example adding together the above examples:
    ---
    settings:
      tests:
        ipv4range:
          dsthost: 8.8.4.4
          dstport: 53
      actions:
        tcp:
          aforder: 4,6
    tests:
      lan:
        ipv4range:
          - 192.168.0.0/24
          - 10.1.2.0/24
    rules:
      hosta:
        - test: lan
          action: tcp4
          tcp4.host: 1.2.3.4
        - action:
            exec:
              - ssh
              - -W
              - '[%h]:%p'
              - 4.3.2.1
      hostb:
        - action: tcp4
          tcp4.host: 4.3.2.1

'''

import sys
import pkgutil

import sshfdpass.actions as actions
import sshfdpass.tests as tests
import sshfdpass.common.config
import sshfdpass.common
from sshfdpass.common.exceptions import *

log = sshfdpass.common.log


_settings={}
_actions={}
_tests={}
_rules={}


def load_config():
    '''
    load_config
    -----------

    Loads configuration. Don't do any sanitization on settings or rules.
    Other steps here:
    * system provided builting tests are initialized
    * system provided actions are initialized
    * config-defined tests parsed and initialized

    Does not expect params.
    Settings are loaded to the module global _settings var.
    Tests are loaded into the module global _tests var.
    Actions are loaded into the module global _actions var.
    Rules are loaded into the module global _rules var.
    '''
    import sshfdpass.common.config
    config = sshfdpass.common.config.read_config(settings=_settings, rules=_rules )
    # Load test modules
    for loader, module_name, is_pkg in pkgutil.walk_packages(tests.__path__):
        if not is_pkg:
            _tests.setdefault(module_name, loader.find_module(module_name).load_module(module_name).Test(**_settings.get('tests',{}).get(module_name,{})))
    # Load action modules
    for loader, module_name, is_pkg in pkgutil.walk_packages(actions.__path__):
        if not is_pkg:
            _actions.setdefault(module_name, loader.find_module(module_name).load_module(module_name).Action(**_settings.get('actions',{}).get(module_name,{})))
    # Load tests from config
    for usertest in config.get('tests',{}):
        _tests.setdefault(usertest, tests.parse_test(config.get('tests',{}).get(usertest), _tests, **_settings.get('tests',{}).get(usertest,{})))


def get_my_rules(host, port, rules):
    '''Provide a list of rules should be applied in run()

    Rule matching system is quite simple at the moment. Only host:port and host keys are looked upon in the dictionary.
    Always add an unconditional tcp action to the end of the list as a fallback option.
    
    Parameters
    ----------
    host: str
        host as we got from the command line
    port: str
        port number as we got it from the command line
    rules: dict
        A dictionary with all the rules coming from the config.

    Returns
    -------
    list
        A list of rules in the order of preference to evaluate.
    '''
    # For some yet unknown reason, this doesn't work on python2:
    #return rules.get('%s:%s'%(host, port), []) + rules.get(host, []) + [ {'action': 'tcp'} ]
    # So, I had to decompose this
    ret = []
    ret += rules.get('%s:%s'%(host, port), []) 
    ret += rules.get(host, []) 
    ret += [ {'action': 'tcp'} ]
    return ret

def get_action_params(rule):
    '''Construct every aspect of the action to run based on the rule content

    An action and it's parameters can be defined in two ways in a rule:
    - action: tcp
      tcp.host: 1.2.3.4

    In this case, the value for the action key in the rule is a simple string.
    All key which starts with the action's name and a dot, will be collected into a dict and passed to the action.
    In this example, the action execution will be called like this:
    execute(host, port, None, {'host': '1.2.3.4'})

    And an action can get actionargs. Let's say, we have an action, called magic, and it has one keyword `wand` with this example config:
    - action:
        magic:
          wand: alice
          book: restricted
      magic.wand: bob
      magic.potion: polijuice

    Than the execution would get these parameters:
    execute(host, port, {'wand': 'alice', 'book': 'restricted'}, {'wand': 'bob', 'potion': 'polijuice'})

    Parameters
    ----------
    rule: dict
        The rule what should be evaluated

    Returns
    -------
    str, args, params
        The first returned argument is the name of the action.
        The second argument is None or the action's argument.
        The third parameter is the dict of the action's parameters.
    '''
    myaction = rule.get('action', sshfdpassMissingAction)
    actionparams = dict()
    actionargs = None
    if isinstance(myaction, str):
        prefix = myaction + '.'
    elif isinstance(myaction, dict):
        if len(myaction.keys()) == 1:
            actionname = list(myaction.keys())[0]
            prefix = actionname + '.'
            actionargs = myaction.get(actionname)
            myaction = actionname
        else:
            raise(sshfdpassException) # Ambigous which action to run
    else:
        raise(sshfdpassException) # An action must be a string or a dict with exactly one key
    for i in rule:
        if i.startswith(prefix):
            actionparams.setdefault(i[len(prefix):], rule.get(i))
    return myaction, actionargs, actionparams

def run():
    '''CLI entry point
    
    This is the entry point for the cli. Does all the job:
    calls load_config()
    then evaluate the rules based on the list got from get_my_rules().
    If there is a test in the rule it will be evaluated.
    If the test evaluation were true or there were no test, we ran the action based on the params parsed by get_action_params().
    '''
    host = sys.argv[1]
    port = sys.argv[2]
    log.message('info', 'sshfdpass is called with host: %s, port: %s'%(host,port))
    load_config()
    for rule in get_my_rules(host, port, _rules):
        log.message('debug','Evaluating rule %s'%(str(rule)))
        action, actionargs, actionparams = get_action_params(rule)
        if 'test' in rule:
            mytest = tests.parse_test(rule.get('test'), _tests)
            if mytest.evaluate():
                return _actions[action].execute(host, port, actionargs, actionparams)
        else:
            return _actions[action].execute(host, port, actionargs, actionparams)
