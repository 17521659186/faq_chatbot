#!/usr/bin/env python
import logging

from tornado import gen

from backend import BaseHandler, route
_logger = logging.getLogger(__name__)

@route(r'/link/test')
class TestLinkHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        """
        用于测试
        """
        echostr = 'ok'
        yield self.write(echostr)