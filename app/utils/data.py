# -*- coding: utf-8 -*-
'''
Created on 2014-07-12
@summary: operate json file
@author: YangHaitao
'''

import sys
import os
import json
import time
import shutil
import logging

from config import CONFIG

LOG = logging.getLogger(__name__)

class DATA(object):
    def __init__(self):
        self.data_file_path = CONFIG["USER_DATA_PATH"]
        self.data_path = os.path.split(CONFIG["USER_DATA_PATH"])[0]
        self.data = {}
        self.changed = False
        if os.path.exists(self.data_path) and os.path.isdir(self.data_path):
            if os.path.exists(self.data_file_path) and os.path.isfile(self.data_file_path):
                fp = open(self.data_file_path, "rb")
                self.data = json.loads(fp.read())
                fp.close()
        else:
            os.makedirs(self.data_path)
            LOG.info("Create path[%s]", self.data_path)

    def refresh(self):
        self.__init__()

    def add(self, key, value):
        result = False
        try:
            self.data[key] = value
            self.changed = True
            LOG.info("Add key[%s] = %s to data", key, value)
        except Exception, e:
            LOG.exception(e)
        return result

    def delete(self, key):
        result = False
        try:
            if self.data.has_key(key):
                self.data.pop(key)
                self.changed = True
            LOG.info("Delete key[%s] from data", key)
        except Exception, e:
            LOG.exception(e)
        return result

    def get(self, key):
        result = False
        try:
            if self.data.has_key(key):
                result = self.data[key]
            LOG.info("Get key[%s] = %s from data", key, result)
        except Exception, e:
            LOG.exception(e)
        return result

    def commit(self):
        result = False
        try:
            if self.changed:
                fp = open(self.data_file_path, "wb")
                fp.write(json.dumps(self.data, indent = 4))
                fp.close()
            LOG.info("Commit data[%s]", self.data_file_path)
        except Exception, e:
            LOG.exception(e)
        return result