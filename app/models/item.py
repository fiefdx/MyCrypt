# -*- coding: utf-8 -*-
'''
Created on 2014-06-17
@summary: item for MyCrypt
@author: YangHaitao
'''

import os
import sys
import struct
import logging
import time
import datetime
import binascii

from utils import sumhash
import tea
from tea import EncryptStr, DecryptStr
from config import CONFIG

cwd = os.path.split(os.path.realpath(__file__))[0]
LOG = logging.getLogger(__name__)
#CRYPT_BLOCK = 1024 * 1024 * 8 # 1024 * 8
CRYPT_BLOCK = 1024 * 8

def get_encrype_length(length):
    fill_n = (8 - (length + 2))%8 + 2
    result = 1 + length + fill_n + 7
    return result

class CryptFile(object):
    def __init__(self, file_path, call_back = None, delay = 0.1):
        '''
        @param call_back: is a function with param process percent. like, call_back(percent). 
        '''
        file_path = os.path.abspath(file_path)
        # LOG.info("Abs file path: %s", file_path)
        self.file_name = os.path.split(file_path)[-1]
        self.file_path = file_path
        self.file_size = 0
        self.file_header = "crypt"
        self.crypt_file_type = ".crypt"
        self.hide_file_type = ".hide"
        self.fname_pos = 0
        self.fname_len = 0
        self.file_pos = 0
        self.file_len = 0
        self.crypt_file_name = ""
        self.crypt_file_path = ""
        self.hide_file_name = ""
        self.hide_file_path = ""
        self.fp = None
        self.call_back = call_back
        self.percent = 0
        self.delay = delay
        self.start_time = 0

    def open_source_file(self):
        if os.path.exists(self.file_path) and os.path.isfile(self.file_path):
            fp = open(self.file_path, "rb")
            fp.seek(0, 2)
            self.file_size = fp.tell()
            fp.seek(0, 0)
            self.fp = fp
            # LOG.info("file size: %s B", self.file_size)
        else:
            error = {"type" : "warning", "info" : "File [%s] dosen't exists!"%self.file_path}
            self.call_back(0, error = error)
            LOG.warning("file path[%s] is not a file!", self.file_path)

    def encrypt(self, key = ""):
        fname_hash = sumhash.sha1sum(self.file_name)
        timestamp = unicode(time.mktime(datetime.datetime.now().timetuple()))
        self.crypt_file_name = sumhash.sha1sum(u"%s%s%s"%(fname_hash, self.file_size, timestamp)) + self.crypt_file_type
        self.crypt_file_path = os.path.join(os.path.split(self.file_path)[0], self.crypt_file_name)
        crypt_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
            LOG.info("crypt_key: %s", crypt_key)
        if not os.path.exists(self.crypt_file_path):
            crypt_fp = open(self.crypt_file_path, "wb")
            LOG.info("Create crypt file path[%s]", self.crypt_file_path)
        else:
            error = {"type" : "warning", "info" : "File [%s] already exists!"%self.crypt_file_path}
            self.call_back(0, error = error)
            LOG.warning("Crypt file path[%s] exists!", self.crypt_file_path)
        if crypt_fp != None and self.fp != None:
            if crypt_key != "":
                if self.call_back:
                    self.call_back(0)
                header_fname = EncryptStr(self.file_name, crypt_key)
                header_fname = binascii.unhexlify(header_fname)
                self.fname_pos = 25
                self.fname_len = len(header_fname)
                self.file_pos = self.fname_pos + self.fname_len
                crypt_fp.write(self.file_header)
                crypt_fp.write(struct.pack(">L", self.fname_pos))
                crypt_fp.write(struct.pack(">L", self.fname_len))
                crypt_fp.write(struct.pack(">L", self.file_pos))
                crypt_fp.write(struct.pack(">Q", self.file_len))
                crypt_fp.write(header_fname)
                crypt_size = 0
                self.start_time = time.time()
                while True:
                    buf = self.fp.read(CRYPT_BLOCK)
                    if not buf:
                        self.fp.close()
                        break
                    crypt_buf = EncryptStr(buf, crypt_key)
                    crypt_buf = binascii.unhexlify(crypt_buf)
                    # LOG.info("write block: %s B", len(crypt_buf))
                    self.file_len += len(crypt_buf)
                    crypt_fp.write(crypt_buf)
                    crypt_size += CRYPT_BLOCK
                    if self.call_back and crypt_size < self.file_size and (time.time() - self.start_time) >= self.delay:
                        percent = crypt_size * 100 / self.file_size
                        if percent > self.percent:
                            self.percent = percent
                            self.start_time = time.time()
                            self.call_back(self.percent)
                crypt_fp.seek(17, 0)
                crypt_fp.write(struct.pack(">Q", self.file_len))
                LOG.info("file pos: %s, file len: %s", self.file_pos, self.file_len)
                # crypt_fp.seek(0, 2)
                if self.call_back:
                    self.call_back(100)
                crypt_fp.close()
            else:
                error = {"type" : "warning", "info" : "Password is empty!"}
                self.call_back(0, error = error)
                LOG.info("Password is empty!")
            self.fp.close()
            # LOG.info("")

    def decrypt(self, key = ""):
        decrypt_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
        if self.fp != None:
            file_header = self.fp.read(5)
            LOG.info("file header: %s", file_header)
            if file_header == self.file_header:
                if crypt_key != "":
                    if self.call_back:
                        self.call_back(0)
                    self.fname_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.fname_len = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_len = struct.unpack(">Q", self.fp.read(8))[0]
                    LOG.info("fname_pos: %s, fname_len: %s, file_pos: %s, file_len: %s", self.fname_pos, self.fname_len, self.file_pos, self.file_len)
                    self.fp.seek(self.fname_pos, 0)
                    file_name = self.fp.read(self.fname_len)
                    file_name = binascii.hexlify(file_name)
                    file_name = DecryptStr(file_name, crypt_key)
                    decrypt_file_path = os.path.join(os.path.split(self.file_path)[0], file_name.decode("utf-8"))
                    if not os.path.exists(decrypt_file_path):
                        decrypt_fp = open(decrypt_file_path, "wb")
                        LOG.info("Create decrypt file path[%s]", decrypt_file_path)
                    else:
                        error = {"type" : "warning", "info" : "File [%s] already exists!"%decrypt_file_path}
                        self.call_back(0, error = error)
                        LOG.warning("Decrypt file path[%s] exists!", decrypt_file_path)
                    crypt_length = get_encrype_length(CRYPT_BLOCK)
                    crypt_size = 0
                    self.start_time = time.time()
                    if decrypt_fp != None:
                        while True:
                            buf = ""
                            if self.file_len < crypt_length:
                                buf = self.fp.read(self.file_len)
                            else:
                                buf = self.fp.read(crypt_length)
                            if not buf:
                                self.fp.close()
                                break
                            self.file_len -= len(buf)
                            decrypt_buf = binascii.hexlify(buf)
                            decrypt_buf = DecryptStr(decrypt_buf, crypt_key)
                            decrypt_fp.write(decrypt_buf)
                            crypt_size += crypt_length
                            if self.call_back and crypt_size < self.file_len and (time.time() - self.start_time) >= self.delay:
                                percent = crypt_size * 100 / self.file_len
                                # self.call_back(percent)
                                if percent > self.percent:
                                    self.percent = percent
                                    self.start_time = time.time()
                                    self.call_back(self.percent)
                            if self.file_len <= 0:
                                break
                        if self.call_back:
                            self.call_back(100)
                        decrypt_fp.close()
                else:
                    error = {"type" : "warning", "info" : "Password is empty!"}
                    self.call_back(0, error = error)
                    LOG.info("Password is empty!")
            else:
                error = {"type" : "warning", "info" : "File [%s] is not a crypt file!"%self.file_path}
                self.call_back(0, error = error)
                LOG.info("The file[%s] is not a crypt file!", self.file_path)
            self.fp.close()

    def decrypt_info(self, key = ""):
        result = ""
        decrypt_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
        if self.fp != None:
            file_header = self.fp.read(5)
            # LOG.info("file header: %s", file_header)
            if file_header == self.file_header:
                if crypt_key != "":
                    self.fname_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.fname_len = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_len = struct.unpack(">Q", self.fp.read(8))[0]
                    # LOG.info("fname_pos: %s, fname_len: %s, file_pos: %s, file_len: %s", self.fname_pos, self.fname_len, self.file_pos, self.file_len)
                    self.fp.seek(self.fname_pos, 0)
                    file_name = self.fp.read(self.fname_len)
                    file_name = binascii.hexlify(file_name)
                    file_name = DecryptStr(file_name, crypt_key)
                    result = file_name
            else:
                LOG.info("The file[%s] is not a crypt file!", self.file_path)
            self.fp.close()
        return result

    def hide(self, key = ""):
        fname_hash = sumhash.sha1sum(self.file_name)
        timestamp = unicode(time.mktime(datetime.datetime.now().timetuple()))
        self.hide_file_name = sumhash.sha1sum(u"%s%s%s"%(fname_hash, self.file_size, timestamp)) + self.hide_file_type
        self.hide_file_path = os.path.join(os.path.split(self.file_path)[0], self.hide_file_name)
        hide_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
            LOG.info("crypt_key: %s", crypt_key)        
        if not os.path.exists(self.hide_file_path):
            hide_fp = open(self.hide_file_path, "wb")
            LOG.info("Create hide file path[%s]", self.hide_file_path)
        else:
            error = {"type" : "warning", "info" : "File [%s] already exists!"%self.hide_file_path}
            self.call_back(0, error = error)
            LOG.error("Hide file path[%s] exists!", self.hide_file_path)
        if hide_fp != None and self.fp != None:
            if crypt_key != "":
                if self.call_back:
                    self.call_back(0)
                header_fname = EncryptStr(self.file_name, crypt_key)
                header_fname = binascii.unhexlify(header_fname)
                # header_fname = self.file_name #must utf-8
                self.fname_pos = 25
                self.fname_len = len(header_fname)
                self.file_pos = self.fname_pos + self.fname_len
                hide_fp.write(self.file_header)
                hide_fp.write(struct.pack(">L", self.fname_pos))
                hide_fp.write(struct.pack(">L", self.fname_len))
                hide_fp.write(struct.pack(">L", self.file_pos))
                hide_fp.write(struct.pack(">Q", self.file_len))
                hide_fp.write(header_fname)
                hide_size = 0
                self.start_time = time.time()
                while True:
                    buf = self.fp.read(CRYPT_BLOCK)
                    if not buf:
                        self.fp.close()
                        break
                    self.file_len += len(buf)
                    hide_fp.write(buf)
                    hide_size += CRYPT_BLOCK
                    if self.call_back and hide_size < self.file_size and (time.time() - self.start_time) >= self.delay:
                        percent = hide_size * 100 / self.file_size
                        # self.call_back(percent)
                        if percent > self.percent:
                            self.percent = percent
                            self.start_time = time.time()
                            self.call_back(self.percent)
                hide_fp.write(self.file_header)
                hide_fp.seek(17, 0)
                hide_fp.write(struct.pack(">Q", self.file_len))
                LOG.info("file pos: %s, file len: %s", self.file_pos, self.file_len)
                if self.call_back:
                    self.call_back(100)
                hide_fp.close()
            else:
                error = {"type" : "warning", "info" : "Password is empty!"}
                self.call_back(0, error = error)
                LOG.info("Password is empty!")
            self.fp.close()

    def show(self, key = ""):
        show_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
        if self.fp != None:
            file_header = self.fp.read(5)
            LOG.info("file header: %s", file_header)
            if file_header == self.file_header:
                if crypt_key != "":
                    if self.call_back:
                        self.call_back(0)
                    self.fname_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.fname_len = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_len = struct.unpack(">Q", self.fp.read(8))[0]
                    LOG.info("fname_pos: %s, fname_len: %s, file_pos: %s, file_len: %s", self.fname_pos, self.fname_len, self.file_pos, self.file_len)
                    self.fp.seek(self.fname_pos, 0)
                    file_name = self.fp.read(self.fname_len)
                    file_name = binascii.hexlify(file_name)
                    file_name = DecryptStr(file_name, crypt_key)
                    # file_name = self.fp.read(self.fname_len)
                    # LOG.debug("file_name: %s, %s, %s", file_name, isinstance(file_name, str), isinstance(file_name, unicode))
                    show_file_path = os.path.join(os.path.split(self.file_path)[0], file_name.decode("utf-8"))
                    if not os.path.exists(show_file_path):
                        show_fp = open(show_file_path, "wb")
                        LOG.info("Create show file path[%s]", show_file_path)
                    else:
                        error = {"type" : "warning", "info" : "File [%s] already exists!"%show_file_path}
                        self.call_back(0, error = error)
                        LOG.error("show file path[%s] exists!", show_file_path)
                    hide_size = 0
                    self.start_time = time.time()
                    if show_fp != None:
                        while True:
                            buf = ""
                            if self.file_len == 0:
                                self.fp.close()
                                break
                            elif self.file_len < CRYPT_BLOCK:
                                buf = self.fp.read(self.file_len)
                            else:
                                buf = self.fp.read(CRYPT_BLOCK)
                            if not buf:
                                self.fp.close()
                                break
                            self.file_len -= len(buf)
                            show_fp.write(buf)
                            hide_size += CRYPT_BLOCK
                            if self.call_back and hide_size < self.file_len and (time.time() - self.start_time) >= self.delay:
                                percent = hide_size * 100 / self.file_len
                                # self.call_back(percent)
                                if percent > self.percent:
                                    self.percent = percent
                                    self.start_time = time.time()
                                    self.call_back(self.percent)
                            if self.file_len <= 0:
                                break
                        if self.call_back:
                            self.call_back(100)
                        show_fp.close()
                else:
                    error = {"type" : "warning", "info" : "Password is empty!"}
                    self.call_back(0, error = error)
                    LOG.info("Password is empty!")
            else:
                error = {"type" : "warning", "info" : "File [%s] is not a hide file!"%self.file_path}
                self.call_back(0, error = error)
                LOG.info("The file[%s] is not a hide file!", self.file_path)
            self.fp.close()

    def show_info(self, key = ""):
        result = ""
        show_fp = None
        crypt_key = ""
        if key != "":
            crypt_key = sumhash.md5twice(key)
        if self.fp != None:
            file_header = self.fp.read(5)
            LOG.info("file header: %s", file_header)
            if file_header == self.file_header:
                if crypt_key != "":
                    if self.call_back:
                        self.call_back(0)
                    self.fname_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.fname_len = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_pos = struct.unpack(">L", self.fp.read(4))[0]
                    self.file_len = struct.unpack(">Q", self.fp.read(8))[0]
                    LOG.info("fname_pos: %s, fname_len: %s, file_pos: %s, file_len: %s", self.fname_pos, self.fname_len, self.file_pos, self.file_len)
                    self.fp.seek(self.fname_pos, 0)
                    file_name = self.fp.read(self.fname_len)
                    file_name = binascii.hexlify(file_name)
                    file_name = DecryptStr(file_name, crypt_key)
                    # file_name = self.fp.read(self.fname_len)
                    result = file_name
            else:
                LOG.info("The file[%s] is not a hide file!", self.file_path)
            self.fp.close()
        return result

class CopyCut(object):
    def __init__(self, source_path, target_path, call_back = None, delay = 0.1):
        self.source_path = source_path
        self.target_path = target_path
        self.call_back = call_back
        self.delay = delay
        self.start_time = 0
        self.file_size = 0
        self.file_len = 0
        self.fp = None
        self.percent = 0

    def open_source_file(self):
        if os.path.exists(self.source_path) and os.path.isfile(self.source_path):
            fp = open(self.source_path, "rb")
            fp.seek(0, 2)
            self.file_size = fp.tell()
            # self.file_len = fp.tell()
            fp.seek(0, 0)
            self.fp = fp
        else:
            error = {"type" : "warning", "info" : "File [%s] dosen't exists!"%self.source_path}
            self.call_back(0, error = error)
            LOG.warning("file path[%s] is not a file!", self.source_path)

    def copy(self):
        result = False
        target_fp = None
        if self.fp != None:
            if os.path.exists(self.target_path):
                error = {"type" : "warning", "info" : "File [%s] already exists!"%self.target_path}
                self.call_back(0, error = error)
                LOG.warning("File [%s] already exists!", self.target_path)
            else:
                target_fp = open(self.target_path, "wb")
                LOG.info("Create copy file[%s]", self.target_path)
            if target_fp != None:
                file_len = self.file_size
                copy_size = 0
                while True:
                    buf = ""
                    if file_len < CRYPT_BLOCK:
                        buf = self.fp.read(file_len)
                    else:
                        buf = self.fp.read(CRYPT_BLOCK)
                    if not buf:
                        self.fp.close()
                        break
                    file_len -= len(buf)
                    target_fp.write(buf)
                    copy_size += CRYPT_BLOCK
                    if self.call_back and copy_size < self.file_size and (time.time() - self.start_time) >= self.delay:
                        percent = copy_size * 100 / self.file_size
                        # self.call_back(percent)
                        if percent > self.percent:
                            self.percent = percent
                            self.start_time = time.time()
                            self.call_back(self.percent)
                    if file_len <= 0:
                        break
                if self.call_back:
                    self.call_back(100)
                target_fp.close()
            self.fp.close()
            LOG.info("Copy [%s] to [%s] success", self.source_path, self.target_path)
            result = True
        return result

    def cut(self):
        flag = self.copy()
        if flag:
            os.remove(self.source_path)
            LOG.info("Cut [%s] to [%s] success", self.source_path, self.target_path)