#

from sshfdpass.common.exceptions import *
from . import logging

log = logging.Logger()

def argparse(arg, rules):
    ret = ''
    status = 0
    if isinstance(arg, str):
        for i in arg:
            if status == 0:
                if i == '%':
                    status = 1
                else:
                    ret += i
            else:
                status = 0
                ret += rules.get(i,i)
        return ret
    raise(sshfdpassException)
