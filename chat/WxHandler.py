import traceback

from tornado import gen
import logging
import json
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from chat.BaseHandler import BaseHandler

_logger = logging.getLogger(__name__)


class MessageHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        user_id = json.loads(self.request.body).get('user_id')
        question = json.loads(self.request.body).get('question')

        intent, response = yield self.application.bot.get_response(user_id, question)

        self.finish(response)
