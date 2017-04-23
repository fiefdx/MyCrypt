# -*- coding: utf-8 -*-
'''
Created on 2014-07-14
@summary: utils for MyCrypt
@author: YangHaitao
'''

import os
import sys
import time
import dateutil
import logging
import datetime
import ctypes
import platform

def get_file_size(size):
    result = ""
    try:
        if size > 1024*1014*1024:
            result = "%.3f G"%(size/1024.0/1024.0/1024.0)
        elif size > 1024*1024:
            result = "%.3f M"%(size/1024.0/1024.0)
        elif size > 1024:
            result = "%.3f K"%(size/1024.0)
        else:
            result = "%d B"%size
    except Exception, e:
        LOG.exception(e)
        result = "0 B"
    return result

def get_free_space_b(path):
    """
    Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize