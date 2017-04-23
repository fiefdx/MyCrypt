# -*- coding: utf-8 -*-
'''
Created on 2013-05-16
@summary: test
@author: YangHaitao
'''

import tornado
import os.path
import logging 
import time

import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen

from config import CONFIG
from base import BaseHandler

LOG = logging.getLogger(__name__)

class TestHandler(BaseHandler):
    def get(self):
        # self.render("search/test.html")
        self.write("this is a test")

class TestIframHandler(BaseHandler):
    def get(self):
        self.render("search/grammar_builder_iframe.html")

class TestFrameHandler(BaseHandler):
    def get(self):
        self.render("search/frame.html")
