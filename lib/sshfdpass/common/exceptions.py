class sshfdpassException(Exception):
    '''Generic sshfdpass Exception class'''
    pass

class sshfdpassUnkownObject(sshfdpassException):
    '''return this type, if you pass an object instance to another object's constructor, but that doesn't recognize the object type as its own, so can't initialize itself'''
    pass

class sshfdpassTargetTypeUnkown(sshfdpassException):
    '''When you define a test, its target must be a list or string which will be auto-converted to a one-element list, but no other data types accepted'''
    pass

class sshfdpassTestUnkown(sshfdpassException):
    '''If you try to define a test based on another test, but that another test is not exists at the point of execution'''
    pass

class sshfdpassTestAmbigous(sshfdpassException):
    '''If you try to define a test based on another test using a dictionary, that dicionary must have exactly one key, the used test's name'''
    pass

class sshfdpassTestParseError(sshfdpassException):
    '''If you try to define a test it can be done via:
        a string, referring another already existing test
        a dict, which has only one key, an already existing test's name'''
    pass

class sshfdpassMissingAction(sshfdpassException):
    '''Every rule must have an action key'''

class sshfdpassAFUnkown(sshfdpassException):
    '''Possible AF values for tcp action is 4 and 6 as in IPv4 and IPv6'''

class sshfdpassActionError(sshfdpassException):
    '''An action on execution must return a true value, otherwise it's considered as an error'''
