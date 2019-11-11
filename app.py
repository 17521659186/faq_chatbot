#!/usr/bin/env python
# coding: utf-8

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
import signal
import logging
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options
from bot import Bot
from chat.WxHandler import MessageHandler
from train.context import PathContext

AsyncHTTPClient.configure(None, max_clients=300)

define("port", default=8899, help="run on th given port", type=int)
define("debug", default=True, help="run in debug mode", type=bool)
define("id", default=0, help="instance id used for multiple processes", type=int)

# Obtain the global Logger
_logger = logging.getLogger(__name__)


def kill_server(sig, frame):
    print("Received signal=%d, quit!" % sig)
    tornado.ioloop.IOLoop.instance().stop()


def main():
    # signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    signal.signal(signal.SIGINT, kill_server)
    # signal.signal(signal.SIGQUIT, kill_server)
    signal.signal(signal.SIGTERM, kill_server)
    # signal.signal(signal.SIGHUP, kill_server)
    ###
    tornado.options.parse_command_line()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s (%(filename)s:%(lineno)d) %(message)s")
    for logHandler in logging.getLogger().handlers:
        logHandler.setFormatter(formatter)

    ###
    app = tornado.web.Application(
        handlers=[
            (r"/chat/bot", MessageHandler)
        ],
        debug=options.debug,
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        static_url_prefix="/static/",
        login_url="/login",
        cookie_secret="This-is-a-COOKIE-SECRET-key, each+ 2017-7-12",
    )




    config = {"version": "0.1", "bot_id": "lancome", "output_dir": "./chat_model/"}
    path_context = PathContext(config)
    app.bot = Bot(path_context, {})


    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(options.port)
    try:
        _logger.info('Server started!')
        # tornado.ioloop.PeriodicCallback(unit.update_access_token, 86400 * 1000).start()
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        _logger.warning(e)
        tornado.ioloop.IOLoop.instance().close()


if __name__ == "__main__":
    main()
    print("welcome to my world")