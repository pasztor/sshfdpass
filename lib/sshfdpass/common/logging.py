import os

class Logger():
    def __init__(self):
        self.logfile=open(os.path.join(os.environ.get('HOME'),'.ssh/fdpass.log'),'a+')
    def message(self,*message):
        # Message start index number
        start = 0
        if len(message) > 1:
            # When we have more than one parameter, the first one is the loglevel, and the other elements can be several loglines with the same loglevel
            level = message[0]
            start = 1
        else:
            level = 'debug'
        for i in message[start:]:
            self.logfile.write('%s: %s\n' % ( level, i))
    def __del__(self):
        self.logfile.close()
