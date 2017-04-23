# -*- coding: utf-8 -*-
'''
Created on 2014-06-18
@summary:  hash utils
@author: YangHaitao
''' 

import sys
import os
import re
import getopt
import logging
import shutil
import datetime
import time
import dateutil
from dateutil import tz
from time import localtime,strftime
import hashlib

from config import CONFIG

cwd = os.path.split(os.path.realpath(__file__))[0]
LOG = logging.getLogger(__name__)

# content must be unicode
def sha1sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha1(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def sha256sum(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.sha256(content.encode("utf-8"))
    m.digest()
    result = m.hexdigest().decode("utf-8")
    return result

def md5twice(content):
    '''
    param content must be unicode
    result is unicode
    '''
    m = hashlib.md5(content.encode("utf-8")).hexdigest()
    result = hashlib.md5(m).hexdigest().decode("utf-8")
    return result
