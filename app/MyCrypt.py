# -*- coding: utf-8 -*-
'''
Created on 2014-06-17
@summary: main
@author: YangHaitao
'''

import os
import os.path
import signal
import logging
import time

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.locale
import tornado.netutil
from tornado.options import define, options

from config import CONFIG
from utils import common
import logger

import modules.bootstrap as bootstrap
import handlers.view as view

LOG = logging.getLogger(__name__)

define("host", default = CONFIG["SERVER_HOST"], help = "run bind the given host", type = str)
define("port", default = CONFIG["SERVER_PORT"], help = "run on the given port", type = int)
define("log", default = "MyCrypt.log", help = "specify the log file", type = str)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", view.ViewHandler),
                    (r"/websocket", view.CryptSocketHandler)]
        settings = dict(
            template_path = os.path.join(CONFIG["APP_PATH"], "templates"),
            static_path = os.path.join(CONFIG["APP_PATH"], "static"),
            ui_modules = [bootstrap,],
            debug = CONFIG["APP_DEBUG"]
            )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    logger.config_logging(file_name = options.log,
                          log_level = CONFIG['LOG_LEVEL'],
                          dir_name = "logs",
                          day_rotate = False,
                          when = "D",
                          interval = 1,
                          max_size = 20,
                          backup_count = 5,
                          console = True)

    LOG.info("MyCrypt Start!")
    tornado.locale.load_translations(os.path.join(CONFIG["APP_PATH"], "translations"))
    http_server = tornado.httpserver.HTTPServer(Application())
    # http_server.listen(options.port)
    # just for localhost & 127.0.0.1
    http_server.listen(options.port, address = "127.0.0.1")
    LOG.info("Listen: localhost:%s", options.port)
    common.Servers.HTTP_SERVER = http_server
    # http_server.bind(options.port, address = "127.0.0.1")
    try:
        signal.signal(signal.SIGTERM, common.sig_handler)
        signal.signal(signal.SIGINT, common.sig_handler)
        tornado.ioloop.IOLoop.instance().start()
    except Exception, e:
        LOG.exception(e)
    finally:
        LOG.info("MyCrypt Exit!")
