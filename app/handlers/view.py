# -*- coding: utf-8 -*-
'''
Created on 2014-07-12
@summary: render encrypt page
@author: YangHaitao
'''

import sys
import os.path
import re
import json
import time
from time import localtime, strftime
import logging
import hashlib
import urllib
import shutil
import chardet
import datetime
import dateutil
from dateutil import tz
import threading

import tornado.web
import psutil

from config import CONFIG
from models.item import CryptFile
from utils.data import DATA
from utils import sumhash
from utils import util
from base import BaseHandler, BaseSocketHandler

LOG = logging.getLogger(__name__)
SocketLock = threading.RLock()
DataLock = threading.RLock()
TaskQueueLock = threading.RLock()

def makekey(c):
    if isinstance(c, (int, long)):
        return c
    elif isinstance(c, (str, unicode)):
        return c.lower()

def listsort(dirs, files, sort_by = "name", desc = False):
    dirs_keys = []
    dirs_tree = {}
    dirs_sort = []
    files_keys = []
    files_tree = {}
    files_sort = []
    for d in dirs:
        dirs_keys.append(d[sort_by])
        if dirs_tree.has_key(d[sort_by]):
            dirs_tree[d[sort_by]].append(d)
        else:
            dirs_tree[d[sort_by]] = []
            dirs_tree[d[sort_by]].append(d)
    dirs_keys = list(set(dirs_keys))
    dirs_keys.sort(key = makekey, reverse = desc)
    # LOG.info("Dirs_keys: %s", dirs_keys)
    n = 1
    for k in dirs_keys:
        for d in dirs_tree[k]:
            d["num"] = n
            d["size"] = util.get_file_size(d["size"])
            dirs_sort.append(d)
            n += 1
    for f in files:
        files_keys.append(f[sort_by])
        if files_tree.has_key(f[sort_by]):
            files_tree[f[sort_by]].append(f)
        else:
            files_tree[f[sort_by]] = []
            files_tree[f[sort_by]].append(f)
    files_keys = list(set(files_keys))
    files_keys.sort(key = makekey, reverse = desc)
    # LOG.info("Files_keys: %s", files_keys)
    for k in files_keys:
        for f in files_tree[k]:
            f["num"] = n
            f["size"] = util.get_file_size(f["size"])
            files_sort.append(f)
            n += 1
    return (dirs_sort, files_sort)

def listdir(dir_path = ".", key = "", sort_by = "name", desc = False):
    dirs = []
    files = []
    try:
        dirs_list = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
        files_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        dirs_list.sort()
        files_list.sort()
        n = 1
        for d in dirs_list:
            d_path = os.path.join(dir_path, d)
            dirs.append({
                "num":n, 
                "name":d, 
                "sha1":sumhash.sha1sum(d_path), 
                "decrypt_name":"", 
                "type":"Directory", 
                "size":os.path.getsize(d_path),
                "ctime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(d_path))),
                "mtime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(d_path)))
            })
            n += 1
        for f in files_list:
            decrypt_name = ""
            if  key != "" and os.path.splitext(f)[-1].lower() == ".crypt":
                file_path = os.path.join(dir_path, f)
                crypt = CryptFile(file_path)
                crypt.open_source_file()
                decrypt_name = crypt.decrypt_info(key)
            elif key != "" and os.path.splitext(f)[-1].lower() == ".hide":
                file_path = os.path.join(dir_path, f)
                crypt = CryptFile(file_path)
                crypt.open_source_file()
                decrypt_name = crypt.show_info(key)
            f_path = os.path.join(dir_path, f)
            files.append({
                "num":n, 
                "name":f, 
                "sha1":sumhash.sha1sum(f_path), 
                "decrypt_name":decrypt_name, 
                "type":os.path.splitext(f)[-1], 
                "size":os.path.getsize(f_path),
                "ctime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(f_path))),
                "mtime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(f_path)))
            })
            n += 1
    except Exception, e:
        LOG.exception(e)
    return listsort(dirs, files, sort_by = sort_by, desc = desc)
    # return (dirs, files)

def joinpath(dir_list):
    dir_path = dir_list[0]
    dir_list = dir_list[1:]
    for d in dir_list:
        dir_path = os.path.join(dir_path, d)
    return dir_path

def splitpath(dir_path):
    dir_list = []
    dir_path, dir_last = os.path.split(dir_path)
    while dir_last != "":
        dir_list.append(dir_last)
        dir_path, dir_last = os.path.split(dir_path)
    dir_list.append(dir_path)
    dir_list.reverse()
    return dir_list

def initpage(home_path, dir_path, columns, scrolltop = False, key = "", sort_by = "name", desc = False):
    disk_usage = psutil.disk_usage(dir_path)
    disk_partitions = psutil.disk_partitions()
    data = {}
    dirs, files = listdir(dir_path = dir_path, key = key, sort_by = sort_by, desc = desc)
    data["cmd"] = "init"
    data["dirs"] = dirs
    data["files"] = files
    data["sort"] = {"name":sort_by, "desc":desc}
    data["dir_path"] = splitpath(dir_path)
    data["home_path"] = splitpath(home_path)
    data["home_path_string"] = home_path
    data["disk_usage"] = {
        "total":util.get_file_size(disk_usage.total),
        "used":util.get_file_size(disk_usage.used),
        "free":util.get_file_size(disk_usage.free),
        "percent":disk_usage.percent
    }
    data["disk_partitions"] = [{"mountpoint":splitpath(p.mountpoint), "device":p.device} for p in disk_partitions]
    p_mountpoint_length = 0
    for n, p in enumerate(data["disk_partitions"]):
        mountpoint_path = joinpath(p["mountpoint"])
        if mountpoint_path in dir_path and len(mountpoint_path) > p_mountpoint_length:
            p_mountpoint_length = len(mountpoint_path)
            data["current_partition"] = n
    data["scrolltop"] = scrolltop;
    data["columns"] = columns
    return data

class DeleteThread(threading.Thread):
    def __init__(self, dir_path, handler, files = [], dirs = [], common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.dirs = dirs
        self.files = files
        self.handler = handler
        self.common_key = common_key
        self.name = "%s_Delete"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        for d in self.dirs:
            try:
                delete_path = os.path.join(self.dir_path, d["name"])
                data = {}
                data["cmd"] = "deleting"
                data["type"] = "dir"
                data["name"] = d["name"]
                data["sha1"] = d["sha1"]
                self.send(json.dumps(data))
                time.sleep(0.1)
                shutil.rmtree(delete_path)
                LOG.info("Delete dir[%s]", delete_path)
                data["cmd"] = "deleted"
                self.send(json.dumps(data))
            except Exception, e:
                LOG.exception(e)
        for f in self.files:
            try:
                delete_path = os.path.join(self.dir_path, f["name"])
                data = {}
                data["cmd"] = "deleting"
                data["type"] = "file"
                data["name"] = f["name"]
                data["sha1"] = f["sha1"]
                self.send(json.dumps(data))
                time.sleep(0.1)
                os.remove(delete_path)
                LOG.info("Delete file[%s]", delete_path)
                data["cmd"] = "deleted"
                self.send(json.dumps(data))
            except Exception, e:
                LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class PasteThread(threading.Thread):
    def __init__(self, dir_path, handler, clipboard, common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.clipboard = clipboard
        self.handler = handler
        self.common_key = common_key
        self.name = "%s_Paste"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        for d in self.clipboard["dirs"]:
            try:
                data = {}
                source_path = os.path.join(self.clipboard["dir_path"], d["name"])
                target_path = os.path.join(self.dir_path, d["name"])
                if os.path.exists(target_path):
                    data["cmd"] = "warning"
                    data["info"] = "Directory [%s] already exists!"%target_path
                    LOG.warning("Dir [%s] already exists!", target_path)
                elif not os.path.exists(source_path) or not os.path.isdir(source_path):
                    data["cmd"] = "warning"
                    data["info"] = "Directory [%s] dosen't exists!"%source_path
                    LOG.warning("Dir [%s] dosen't exists!", source_path)
                else:
                    if self.clipboard["type"] == CryptSocketHandler.CUT:
                        shutil.move(source_path, target_path)
                        data["info"] = "Cut dir [%s] to [%s] success"%(source_path, target_path)
                        LOG.info("Cut dir [%s] to [%s] success", source_path, target_path)
                    elif self.clipboard["type"] == CryptSocketHandler.COPY:
                        shutil.copytree(source_path, target_path)
                        data["info"] = "Copy dir [%s] to [%s] success"%(source_path, target_path)
                        LOG.info("Copy dir [%s] to [%s] success", source_path, target_path)
                    time.sleep(0.1)
                    LOG.info("Paste dir [%s] to [%s]", source_path, target_path)
                #     data["cmd"] = "pasted"
                #     data["type"] = "dir"
                #     data["sha1"] = sumhash.sha1sum(target_path)
                #     data["name"] = d["name"]
                self.send(json.dumps(data))
            except Exception, e:
                LOG.exception(e)
        for f in self.clipboard["files"]:
            try:
                data = {}
                source_path = os.path.join(self.clipboard["dir_path"], f["name"])
                target_path = os.path.join(self.dir_path, f["name"])
                if os.path.exists(target_path):
                    data["cmd"] = "warning"
                    data["info"] = "File [%s] already exists!"%target_path
                    LOG.warning("File [%s] already exists!", target_path)
                elif not os.path.exists(source_path) or not os.path.isfile(source_path):
                    data["cmd"] = "warning"
                    data["info"] = "File [%s] dosen't exists!"%source_path
                    LOG.warning("File [%s] dosen't exists!", source_path)
                else:
                    if self.clipboard["type"] == CryptSocketHandler.CUT:
                        shutil.move(source_path, target_path)
                        data["info"] = "Cut file [%s] to [%s] success"%(source_path, target_path)
                        LOG.info("Cut file [%s] to [%s] success", source_path, target_path)
                    elif self.clipboard["type"] == CryptSocketHandler.COPY:
                        shutil.copy(source_path, target_path)
                        data["info"] = "Copy file [%s] to [%s] success"%(source_path, target_path)
                        LOG.info("Copy file [%s] to [%s] success", source_path, target_path)
                    time.sleep(0.1)
                    LOG.info("Paste file [%s] to [%s]", source_path, target_path)
                #     data["cmd"] = "pasted"
                #     data["sha1"] = sumhash.sha1sum(target_path)
                #     data["type"] = "file"
                #     data["name"] = f["name"]
                self.send(json.dumps(data))
            except Exception, e:
                LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class EncryptThread(threading.Thread):
    def __init__(self, dir_path, file_name, sha1, handler, key, common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.file_name = file_name
        self.sha1 = sha1
        self.handler = handler
        self.key = key
        self.common_key = common_key
        self.name = "%s_Encrypt"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        try:
            file_path = os.path.join(self.dir_path, self.file_name)
            crypt = CryptFile(file_path, call_back = self.process)
            crypt.open_source_file()
            crypt.encrypt(self.key)
        except Exception, e:
            LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def process(self, percent, error = None):
        data = {}
        if error == None:
            data["cmd"] = "encrypting"
            data["percent"] = percent
            data["sha1"] = self.sha1
            data["name"] = self.file_name
            LOG.info("Encrypt: %s%%", percent)
        else:
            data["cmd"] = error["type"]
            data["info"] = error["info"]
        self.send(json.dumps(data))

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class DecryptThread(threading.Thread):
    def __init__(self, dir_path, file_name, sha1, handler, key, common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.file_name = file_name 
        self.sha1 = sha1
        self.handler = handler
        self.key = key
        self.common_key = common_key
        self.name = "%s_Decrypt"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        try:
            file_path = os.path.join(self.dir_path, self.file_name)
            crypt = CryptFile(file_path, call_back = self.process)
            crypt.open_source_file()
            crypt.decrypt(self.key)
        except Exception, e:
            LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def process(self, percent, error = None):
        data = {}
        if error == None:
            data["cmd"] = "decrypting"
            data["percent"] = percent
            data["sha1"] = self.sha1
            data["name"] = self.file_name
        else:
            data["cmd"] = error["type"]
            data["info"] = error["info"]
        self.send(json.dumps(data))

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class HideThread(threading.Thread):
    def __init__(self, dir_path, file_name, sha1, handler, key, common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.file_name = file_name
        self.sha1 = sha1
        self.handler = handler
        self.key = key
        self.common_key = common_key
        self.name = "%s_Hide"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        try:
            file_path = os.path.join(self.dir_path, self.file_name)
            crypt = CryptFile(file_path, call_back = self.process)
            crypt.open_source_file()
            crypt.hide(self.key)
        except Exception, e:
            LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def process(self, percent, error = None):
        data = {}
        if error == None:
            data["cmd"] = "hiding"
            data["percent"] = percent
            data["sha1"] = self.sha1
            data["name"] = self.file_name
        else:
            data["cmd"] = error["type"]
            data["info"] = error["info"]
        self.send(json.dumps(data))

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class ShowThread(threading.Thread):
    def __init__(self, dir_path, file_name, sha1, handler, key, common_key = "", sort_by = "name", desc = False):
        threading.Thread.__init__(self)
        self.dir_path = dir_path
        self.file_name = file_name 
        self.sha1 = sha1
        self.handler = handler
        self.key = key
        self.common_key = common_key
        self.name = "%s_Show"%strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.status = "Waiting"
        self.sort_by = sort_by
        self.desc = desc

    def run(self):
        self.status = "Running"
        try:
            file_path = os.path.join(self.dir_path, self.file_name)
            crypt = CryptFile(file_path, call_back = self.process)
            crypt.open_source_file()
            crypt.show(self.key)
        except Exception, e:
            LOG.exception(e)
        time.sleep(0.1)
        DataLock.acquire()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        DataLock.release()
        data = initpage(home_path, self.dir_path, columns, key = self.common_key, sort_by = self.sort_by, desc = self.desc)
        self.send(json.dumps(data))
        self.status = "Done"

    def process(self, percent, error = None):
        data = {}
        if error == None:
            data["cmd"] = "showing"
            data["percent"] = percent
            data["sha1"] = self.sha1
            data["name"] = self.file_name
        else:
            data["cmd"] = error["type"]
            data["info"] = error["info"]
        self.send(json.dumps(data))

    def send(self, msg):
        try:
            SocketLock.acquire()
            self.handler.write_message(msg)
            SocketLock.release()
        except Exception, e:
            LOG.exception(e)

class TaskManagerThread(threading.Thread):
    def __init__(self, max_task = 2, time_delta = 2):
        threading.Thread.__init__(self)
        self.run_task = []
        self.max_task = max_task
        self.time_delta = time_delta
        self.status_flag = False

    def run(self):
        try:
            while True:
                data = {}
                done_task = []
                if self.status_flag:
                    data["cmd"] = "status"
                    data["tasks"] = []
                    for task in self.run_task:
                        data["tasks"].append({"name":task.name, "status":task.status})
                    TaskQueueLock.acquire()
                    for task in CryptSocketHandler.TASKS:
                        data["tasks"].append({"name":task.name, "status":task.status})
                    TaskQueueLock.release()
                    send_msgs(json.dumps(data), CryptSocketHandler.socket_handlers)
                    # LOG.info("Send status")
                # LOG.info("TaskManager: Running")
                for task in self.run_task:
                    if task.status == "Done":
                        done_task.append(task)
                        LOG.info("Task: %s is Done", task.name)
                for task in done_task:
                    self.run_task.remove(task)
                add_task_num = self.max_task - len(self.run_task)
                # LOG.info("run_task: %s, add_task_num: %s", self.run_task, add_task_num)
                if add_task_num > 0:
                    TaskQueueLock.acquire()
                    while add_task_num > 0 and len(CryptSocketHandler.TASKS) > 0:
                        LOG.info("task: %s, add_task_num: %s", CryptSocketHandler.TASKS, add_task_num)
                        task = CryptSocketHandler.TASKS.pop(0)
                        task.start()
                        self.run_task.append(task)
                        add_task_num -= 1
                    TaskQueueLock.release()
                time.sleep(self.time_delta)
        except Exception, e:
            LOG.exception(e)

    def enable_status(self, flag = False):
        self.status_flag = flag

class ViewHandler(BaseHandler):
    USER_DATA = DATA()
    def get_user_locale(self):
        ViewHandler.USER_DATA.refresh()
        user_locale = ViewHandler.USER_DATA.get("LANGUAGE")
        if user_locale:
            return tornado.locale.get(user_locale)
        return None

    def get(self):
        ViewHandler.USER_DATA.refresh()
        user_locale = ViewHandler.USER_DATA.get("LANGUAGE")
        if not user_locale:
            user_locale = "en_US"
        self.render("crypt.html", user_locale = user_locale)

def send_msg(msg, handler):
    try:
        handler.write_message(msg)
    except Exception, e:
        LOG.exception(e)

def send_msgs(msg, handlers):
    try:
        for handler in handlers:
            handler.write_message(msg)
    except Exception, e:
        LOG.exception(e)

class CryptSocketHandler(BaseSocketHandler):
    SET = "set"
    STATUS = "status"
    REFRESH = "refresh"
    CD = "cd"
    RENAME = "rename"
    DELETE = "delete"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    HIDE = "hide"
    SHOW = "show"
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"
    USER_DATA = DATA()
    PASSWORD = ""
    CLIPBOARD = {}
    TASKS = []
    TaskManager = None
    SORT = {"name":"name", "desc":False}
    socket_handlers = set()

    def get_user_locale(self):
        ViewHandler.USER_DATA.refresh()
        user_locale = ViewHandler.USER_DATA.get("LANGUAGE")
        if user_locale:
            return tornado.locale.get(user_locale)
        return None

    def open(self):
        if CryptSocketHandler.TaskManager == None:
            CryptSocketHandler.TaskManager = TaskManagerThread(max_task = 2, time_delta = 1)
            CryptSocketHandler.TaskManager.daemon = True
            CryptSocketHandler.TaskManager.start()
        CryptSocketHandler.USER_DATA.refresh()
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        language = CryptSocketHandler.USER_DATA.get("LANGUAGE")
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        if not home_path:
            CryptSocketHandler.USER_DATA.add("HOME_PATH", CONFIG["HOME_PATH"])
            CryptSocketHandler.USER_DATA.commit()
            CryptSocketHandler.USER_DATA.refresh()
            home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        LOG.info("trans: %s", self.locale.translate("Name").encode("utf-8"))
        if not columns:
            CryptSocketHandler.USER_DATA.add("COLUMNS", 
                [{"value":"#", "trans":"#", "key":"num", "display":True}, 
                {"value":"Name", "trans":u"名称", "key":"name", "display":True},
                {"value":"Decrypt Name", "trans":u"解密后名称", "key":"decrypt_name", "display":False},
                {"value":"Type", "trans":u"类型", "key":"type", "display":True}, 
                {"value":"Size", "trans":u"大小", "key":"size", "display":True},
                {"value":"Date Modified", "trans":u"修改日期", "key":"mtime", "display":True}])
            CryptSocketHandler.USER_DATA.commit()
            CryptSocketHandler.USER_DATA.refresh()
            columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        data = {}
        if self not in CryptSocketHandler.socket_handlers:
            CryptSocketHandler.socket_handlers.add(self)
            LOG.info("crypt websocket len: %s", len(CryptSocketHandler.socket_handlers))
        else:
            LOG.info("crypt websocket len: %s", len(CryptSocketHandler.socket_handlers))
        if home_path:
            sort = CryptSocketHandler.SORT
            data = initpage(home_path, home_path, columns, key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            send_msg(json.dumps(data), self)

    def on_close(self):
        CryptSocketHandler.socket_handlers.remove(self)
        LOG.info("crypt websocket len: %s", len(CryptSocketHandler.socket_handlers))

    def on_message(self, msg):
        msg = json.loads(msg)
        LOG.info("msg: %s", msg)
        data = {}
        sort = CryptSocketHandler.SORT
        CryptSocketHandler.USER_DATA.refresh()
        columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
        home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
        language = CryptSocketHandler.USER_DATA.get("LANGUAGE")
        if msg["cmd"] == CryptSocketHandler.SET:
            password = ""
            home_path_tmp = ""
            language_tmp = ""
            columns_tmp = []
            refresh = False
            if msg["password"] != "":
                password = msg["password"]
                CryptSocketHandler.PASSWORD = password
            if msg["home_path"] != "":
                home_path_tmp = msg["home_path"]
                if home_path != home_path_tmp and os.path.exists(home_path) and os.path.isdir(home_path):
                    CryptSocketHandler.USER_DATA.add("HOME_PATH", home_path_tmp)
            if msg["language"] != "":
                language_tmp = msg["language"]
                if language != language_tmp:
                    CryptSocketHandler.USER_DATA.add("LANGUAGE", language_tmp)
                    refresh = True
                    data["cmd"] = "refresh"
            if msg["columns"] != []:
                columns_tmp = msg["columns"]
                if columns != columns_tmp:
                    CryptSocketHandler.USER_DATA.add("COLUMNS", columns_tmp)
            CryptSocketHandler.USER_DATA.commit()
            if refresh:
                send_msgs(json.dumps(data), CryptSocketHandler.socket_handlers)
            else:
                CryptSocketHandler.USER_DATA.refresh()
                columns = CryptSocketHandler.USER_DATA.get("COLUMNS")
                home_path = CryptSocketHandler.USER_DATA.get("HOME_PATH")
                dir_path = joinpath(msg["dir_path"])
                # sort = CryptSocketHandler.SORT
                data = initpage(home_path, dir_path, columns, key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
                send_msgs(json.dumps(data), CryptSocketHandler.socket_handlers)
        elif msg["cmd"] == CryptSocketHandler.STATUS:
            CryptSocketHandler.TaskManager.enable_status(flag = msg["enable"])
        elif msg["cmd"] == CryptSocketHandler.REFRESH:
            dir_path = joinpath(msg["dir_path"])
            sort = msg["sort"]
            CryptSocketHandler.SORT = sort
            data = initpage(home_path, dir_path, columns, key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            send_msg(json.dumps(data), self)
        elif msg["cmd"] == CryptSocketHandler.CD:
            cd_path = joinpath(msg["dir_path"])
            # sort = CryptSocketHandler.SORT
            data = initpage(home_path, cd_path, columns, scrolltop = True, key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            send_msg(json.dumps(data), self)
        elif msg["cmd"] == CryptSocketHandler.RENAME:
            dir_path = joinpath(msg["dir_path"])
            old_name = msg["old_name"]
            new_name = msg["new_name"]
            if new_name != "" and new_name != old_name:
                old_path = os.path.join(dir_path, old_name)
                new_path = os.path.join(dir_path, new_name)
                if os.path.exists(new_path):
                    data["cmd"] = "warning"
                    data["info"] = "File [%s] already exists!"%new_path
                else:
                    os.rename(old_path, new_path)
                    # sort = CryptSocketHandler.SORT
                    data = initpage(home_path, dir_path, columns, key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
                send_msg(json.dumps(data), self)
        elif msg["cmd"] == CryptSocketHandler.DELETE:
            dir_path = joinpath(msg["dir_path"])
            TaskQueueLock.acquire()
            delete_thread = DeleteThread(dir_path, self, files = msg["files"], dirs = msg["dirs"], common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(delete_thread)
            TaskQueueLock.release()
            # delete_thread.start()
        elif msg["cmd"] == CryptSocketHandler.ENCRYPT:
            dir_path = joinpath(msg["dir_path"])
            file_name = msg["file_name"]
            key = msg["password"]
            sha1 = msg["sha1"]
            import chardet
            LOG.info("Type: %s, %s", type(dir_path), type(file_name))
            # LOG.info("Chardet: %s, %s", chardet.detect(file_name), chardet.detect(dir_path))
            TaskQueueLock.acquire()
            encrypt_thread = EncryptThread(dir_path, file_name, sha1, self, key, common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(encrypt_thread)
            # encrypt_thread.start()
            TaskQueueLock.release()
            # LOG.info("Thread Start")
            # encrypt_thread.start()
        elif msg["cmd"] == CryptSocketHandler.DECRYPT:
            dir_path = joinpath(msg["dir_path"])
            file_name = msg["file_name"]
            key = msg["password"]
            sha1 = msg["sha1"]
            TaskQueueLock.acquire()
            decrypt_thread = DecryptThread(dir_path, file_name, sha1, self, key, common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(decrypt_thread)
            TaskQueueLock.release()
            # decrypt_thread.start()
        elif msg["cmd"] == CryptSocketHandler.HIDE:
            dir_path = joinpath(msg["dir_path"])
            file_name = msg["file_name"]
            key = msg["password"]
            sha1 = msg["sha1"]
            TaskQueueLock.acquire()
            hide_thread = HideThread(dir_path, file_name, sha1, self, key, common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(hide_thread)
            TaskQueueLock.release()
            # hide_thread.start()
        elif msg["cmd"] == CryptSocketHandler.SHOW:
            dir_path = joinpath(msg["dir_path"])
            file_name = msg["file_name"]
            key = msg["password"]
            sha1 = msg["sha1"]
            TaskQueueLock.acquire()
            show_thread = ShowThread(dir_path, file_name, sha1, self, key, common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(show_thread)
            TaskQueueLock.release()
            # show_thread.start()
        elif msg["cmd"] == CryptSocketHandler.COPY:
            dir_path = joinpath(msg["dir_path"])
            files = msg["files"]
            dirs = msg["dirs"]
            CryptSocketHandler.CLIPBOARD["type"] = CryptSocketHandler.COPY
            CryptSocketHandler.CLIPBOARD["dir_path"] = dir_path
            CryptSocketHandler.CLIPBOARD["files"] = files
            CryptSocketHandler.CLIPBOARD["dirs"] = dirs
            data["cmd"] = "paste"
            send_msgs(json.dumps(data), CryptSocketHandler.socket_handlers)
        elif msg["cmd"] == CryptSocketHandler.CUT:
            dir_path = joinpath(msg["dir_path"])
            files = msg["files"]
            dirs = msg["dirs"]
            CryptSocketHandler.CLIPBOARD["type"] = CryptSocketHandler.CUT
            CryptSocketHandler.CLIPBOARD["dir_path"] = dir_path
            CryptSocketHandler.CLIPBOARD["files"] = files
            CryptSocketHandler.CLIPBOARD["dirs"] = dirs
            data["cmd"] = "paste"
            send_msgs(json.dumps(data), CryptSocketHandler.socket_handlers)
        elif msg["cmd"] == CryptSocketHandler.PASTE:
            dir_path = joinpath(msg["dir_path"])
            TaskQueueLock.acquire()
            paste_thread = PasteThread(dir_path, self, CryptSocketHandler.CLIPBOARD, common_key = CryptSocketHandler.PASSWORD, sort_by = sort["name"], desc = sort["desc"])
            CryptSocketHandler.TASKS.append(paste_thread)
            TaskQueueLock.release()
            # paste_thread.start()



