# -*- coding: utf-8 -*-
'''
Created on 2013-10-26 21:29
@summary:  import yaml configuration
@author: YangHaitao
''' 
try:
    import yaml
except ImportError:
    raise ImportError("Config module requires pyYAML package, please check if pyYAML is installed!")

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import os
#
# default config
cwd = os.path.split(os.path.realpath(__file__))[0]
configpath = os.path.join(cwd, "configuration.yml")

def update(**kwargs):
    config = load(stream = file(configpath), Loader = Loader)
    for k in kwargs:
        if k in config:
            config[k] = kwargs[k]
    fp = open(configpath, "wb")
    dump(config, fp, default_flow_style = False)
    fp.close()

CONFIG = {}
try:
    # script in the app dir
    localConf = load(stream = file(configpath), Loader = Loader)
    CONFIG.update(localConf)
    if not CONFIG.has_key("APP_PATH"):
        CONFIG["APP_PATH"] = cwd
    if not CONFIG.has_key("HOME_PATH"):
        CONFIG["HOME_PATH"] = os.path.expanduser("~")
    if not CONFIG.has_key("USER_DATA_PATH"):
        CONFIG["USER_DATA_PATH"] = os.path.join(os.path.split(cwd)[0], "data/data.json")
except Exception, e:
    print e

if __name__ == "__main__":
    print "CONFIG: %s"%CONFIG
