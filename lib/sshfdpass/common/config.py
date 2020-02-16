import os
import sshfdpass.common
log = sshfdpass.common.log

try:
    No_Module = ModuleNotFoundError
except NameError:
    No_Module = ImportError

def read_config(conffile=os.path.join(os.environ.get('HOME'), '.ssh/fdpass.conf'), settings={}, rules={}):
    try:
        import yaml
        confloader = yaml.safe_load
    except No_Module:
        import json
        confloader = json.load
    try:
        with open(conffile, 'r') as conffd:
            config = confloader(conffd)
    except FileNotFoundError:
        config = dict()
    if isinstance(config.get('settings'),dict):
        log.message('debug','Settings loaded')
        settings.update(config.get('settings'))
    else:
        log.message('warning','settings is not dict, so I replace it with an empty dict')
        config['settings'] = dict()
    if isinstance(config.get('rules'),dict):
        log.message('debug', 'rules loaded')
        rules.update(config.get('rules'))
    else:
        log.message('warning', 'rules is not a dict or empty, so I fill it up with an empty dict')
        config['rules'] = dict()
    return config
