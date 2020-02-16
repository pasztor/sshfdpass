#

'''
sshfdpass.tests
---------------

This package should provide a base for your own tests.
It provides an AbstractTest baseclass for your own testclasses.

It also provides a parse_test() function to parse the tests defined in the config.
'''

import sshfdpass.common
from sshfdpass.common.exceptions import *

log = sshfdpass.common.log

class AbstractTest():
    '''
    A class ment to be the base class for all tests.

    Every Test name must be uniq, no matter if the test is a builtin or a user-defined one.
    Upon initialization every test is instanciated, and it get's it's parameters from it's settings and it's parent test if it has any.

    Builtin tests will get their kwargs from settings.

    User defined tests will get their kwargs from settings as well, but the `target` of user defined tests can be defined inline.
    A test's `target` must always be a list.
    There is one exception when the value associated with the test's name is a string, than that string will be converted to a one-element list, containing that string.
    Ergo this definitions inside tests will be equal:
    lan:
      ipv4range: 192.168.0.0/24

    lan:
      ipv4range: [ 192.168.0.0/24 ]

    lan:
      ipv4range:
        - 192.168.0.0/24
      
    Attributes
    ----------
    result: None or boolean
        If the test was not evaluated earlier, than it is None. If it was evaluated already, it caches the result here
    cache: dict
        Provide cache for instances. Typical usage ipv4range evaluation: It's enough to find out my own ip once.
    settings: dict
        Settings of this test

    Methods
    -------
    __init__(self, *args, **kwargs)
        class constructor
    settings(self):
        property getter
    _evaluate(self, **kwargs)
        This should be redefined in child classes. This is the actual method which gives back the verdict of the test
    _defaults(self)
        This should be redefined in child classes to return a dict with the objects' default settings in case we have to operate with default settings.
    evaluate(self, **kwargs)
        This should be not redefined. This is the wrapper to call _evaluate()
    '''
    def __init__(self, *args, **kwargs):
        '''
        Parameters
        ----------
        args: list
            parent test, or empty
        kwargs: dict
            test settings
        '''
        self.result = None
        self.cache = dict()
        self._settings = self._defaults()
        for arg in args:
            if isinstance(self, type(arg)):
                self._settings.update(arg.__getattribute__('settings'))
        self._settings.update(kwargs)

    @property
    def settings(self):
        '''
        Simple property getter
        '''
        return self._settings

    def _evaluate(self, **kwargs):
        return False

    def _defaults(self):
        return dict()

    def evaluate(self, **kwargs):
        '''
        Wrapper to evaluate the test. You can override settings on-demand with kwargs.
        The actual evaluator function should be defined in child classes in the _evaluate() method.
        '''
        log.message('evaluating test %s (%s, %s)'%(type(self), self.settings, kwargs))
        if kwargs == {}:
            # If no local override for evaluation and no cached result yet, we should do the actual evaluation
            if self.result is None:
                self.result = self._evaluate()
        else:
            # In case of casual parameters we won't cache the endresult
            return self._evaluate(**kwargs)
        log.message('returning cached value')
        return self.result



def parse_test(testdef, alltests, **kwargs):
    '''Parse a user defined test

    User defined tests can happen in two ways:
    In the test definitions, which is a dict, where the key is the defined test's name
    and the value is the tests' definition
    Or inline within the rules. In that case, the test won't have a name in the
    regiestered tests later.

    A test could be defined several ways:
    
    If it's a string, than it should be based on an already defined test.
    Parameters might be override using kwargs.
    This is why I needed the *args into the AbstractTest class' constructor.
    
    If it's a dict, than it must have one key only:
    That one key is the name of the test the newly defined test should be based on.
    The value must be either a dict or a list.
    If the value is a string, it will be auto-converted into a one-element list.
    The value-list will be passed to the test as the "target" attribute.

    To be able to base the newly created test on an already existing one, this
    function requires access to the already defined tests' dict.

    Parameters
    ----------

    testdef: dict/str
        The test definition to be parsed
    alltests: dict
        The dict of all already registered tests
    kwargs: dict
        Parameters to override compared to the parent test this new test is based on.

    Returns
    -------

        A test object. An instance of one descendant of the AbstractTest class.
    '''
    log.message('parsing test (%s, %s)'%(testdef, kwargs))
    if isinstance(testdef, dict):
        if len(testdef.keys()) == 1:
            testname = list(testdef.keys())[0]
            testvalue = testdef.get(testname)
            if testname in alltests:
                if isinstance(testvalue, list):
                    return type(alltests[testname])(alltests[testname], target=testvalue, **kwargs)
                elif isinstance(testdef.get(testname), str):
                    return type(alltests[testname])(alltests[testname], target=[testvalue], **kwargs)
                else:
                    raise(sshfdpassTargetTypeUnkown)
            else:
                log.message('debug', 'testname: %s'%(testname))
                log.message('debug', 'target: %s'%(target))
                log.message('debug', 'already defined tests: %s'%(alltests))
                raise(sshfdPassTestUnkown)
        else:
            raise(sshfdpassTestAmbigous)
    elif isinstance(testdef, str):
        if testdef in alltests:
            return alltests.get(testdef)
        else:
            raise(sshfdpassTestUnkown)
    else:
        raise(sshfdpassTestParseError)


