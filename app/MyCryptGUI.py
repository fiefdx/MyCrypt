#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2015-03-28
@summary: main
@author: YangHaitao
'''

import os
import os.path
import logging
import signal
import time
from threading import Timer, RLock, Thread

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.locale
import tornado.netutil
from tornado.options import define, options
import wx

from config import CONFIG, update
from utils import common
import logger

import modules.bootstrap as bootstrap
import handlers.view as view

TRAY_TOOLTIP = "MyCrypt(%s)" % CONFIG["SERVER_PORT"]
TRAY_ICON = os.path.join(CONFIG["APP_PATH"], "static/mycrypt.ico")

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

class WebServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.ioloop_instance = None

    def run(self):
        tornado.locale.load_translations(os.path.join(CONFIG["APP_PATH"], "translations"))
        http_server = tornado.httpserver.HTTPServer(Application())
        # http_server.listen(options.port)
        # just for localhost & 127.0.0.1
        http_server.listen(options.port, address = "127.0.0.1")
        LOG.info("Listen: localhost:%s", options.port)
        common.Servers.HTTP_SERVER = http_server
        # http_server.bind(options.port, address = "127.0.0.1")
        try:
            self.ioloop_instance = tornado.ioloop.IOLoop.instance()
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:
            LOG.exception(e)
        finally:
            LOG.info("IOLoop instance Exit!")

    def close(self):
        deadline = time.time() + common.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
        LOG.info("Will shutdown in %s seconds ...", common.MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        def stop_loop():
            now = time.time()
            if now < deadline and (self.ioloop_instance._callbacks or self.ioloop_instance._timeouts):
                self.ioloop_instance.add_timeout(now + 1, stop_loop)
            else:
                self.ioloop_instance.stop()
                LOG.info("MyCrypt(%s:%s) Shutdown!", CONFIG["SERVER_HOST"], CONFIG["SERVER_PORT"])

        stop_loop()

def restart_program():
    """
    Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function.
    """
    common.sig_thread_handler(signal.SIGINT, None)
    python = sys.executable
    LOG.debug("restart cmd: %s, %s", python, sys.argv)
    time.sleep(3)
    os.execl(python, python, * sys.argv)

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id = item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.preference = None
        # self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Preference', self.on_preference)
        create_menu_item(menu, 'Restart', self.on_restart)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        # print 'Tray icon was left-clicked.'
        pass

    def on_preference(self, event):
        w = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        h = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        if not self.preference:
            self.preference = PreferenceFrame("Preference", (w / 2 - 90, h / 2 - 140), (180, -1))
            self.preference.Show()

    def on_restart(self, event):
        restart_program()

    def on_exit(self, event):
        common.sig_thread_handler(signal.SIGINT, None)
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class PreferenceFrame(wx.Frame):
    def __init__(self, title, pos, size):
        wx. Frame.__init__(self, None, -1, title, pos, size, style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        # self.panel = wx.Panel(self, -1, size = (180, 280))
        self.te_server_port = None

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.panel)
        self.set_textctrl()
        self.set_button()
        self.sizer.AddSpacer(10)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Fit()

    def set_textctrl(self):
        self.te_server_port = wx.TextCtrl(self, -1, str(CONFIG["SERVER_PORT"]))
        sizer = wx.FlexGridSizer(cols = 2, hgap = 6, vgap = 6)
        sizer.AddMany([self.te_server_port])
        box = self.MakeStaticBoxSizer("Server Port", [sizer])
        self.sizer.Add(box, 0, wx.ALL, 10)

    def set_button(self):
        self.save_button = wx.Button(self, -1, label = "Save")
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save_button)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.save_button, 0, wx.RIGHT | wx.BOTTOM)
        self.sizer.Add(sizer, 0, wx.ALIGN_CENTER)

    def MakeStaticBoxSizer(self, boxlabel, items):
        box = wx.StaticBox(self, -1, boxlabel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        for item in items:
            sizer.Add(item, 0, wx.ALL, 2)
        return sizer

    def OnSave(self, event):
        values = {}
        if self.te_server_port:
            try:
                v = int(self.te_server_port.GetValue())
                values["SERVER_PORT"] = v
            except Exception, e:
                LOG.exception(e)
        update(**values)
        self.Destroy()

    def OnQuit(self, event):
        self.Close()

class App(wx.App):
    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

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
    webserver = WebServer()
    common.Servers.WEB_SERVER = webserver
    signal.signal(signal.SIGTERM, common.sig_thread_handler)
    signal.signal(signal.SIGINT, common.sig_thread_handler)
    webserver.daemon = True
    webserver.start()
    try:
        app = App(False)
        app.MainLoop()
    except Exception, e:
        LOG.exception(e)
    LOG.info("MyCrypt Exit!")
