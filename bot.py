#!/usr/bin/env python
# coding:utf-8
# !/usr/bin/env python
# coding:utf-8
import asyncio
import inspect
import json
import os
import random
import sys
from faq.tfidf_legreg.classfier import TFIDFClassfier
from settings.setting import DEFAULT_RESP
from train.context import PathContext


class Bot(object):
    def __init__(self, path_context, kwargs):
        self.kwargs = kwargs
        self.context = path_context
        self.intrepreter = None
        self.agent = None
        self.faq = None
        self.settings = None
        self.init_path()
        self.reload()

    def init_path(self):
        sys.path.insert(0, self.context.model_output_path)

    def reload(self):
        if os.path.exists(self.context.faq_model_output_path):
            # self.faq = AnyQModule({"path_context": self.context})
            self.faq = TFIDFClassfier(self.context)
            self.faq.load()
        if os.path.exists(self.context.settings_path):
            with open(self.context.settings_path, "r") as f:
                self.settings = json.load(f)

    def get_config(self, key, default):
        return self.kwargs.get(key, default)

    def get_default_resp(self):
        if self.settings:
            default_resp = self.settings.get("default_resp", None)
            if default_resp:
                return random.choice(default_resp)
            else:
                return DEFAULT_RESP

    async def get_response(self, user_id, question):
        intent = None
        response = None

        if self.agent:
            intent, response = await self.agent.get_response(question, user_id)

        if not response and self.faq:
            if inspect.iscoroutinefunction(self.faq.predict):
                response, score = await self.faq.predict(self.context.bot_id, user_id, question)
            else:
                response, score = self.faq.predict(self.context.bot_id, user_id, question)
            intent = "FAQ"

        if not response:
            response = self.get_default_resp()

        return (intent, response)


if __name__ == "__main__":
    import argparse

    # parser = argparse.ArgumentParser(description='Command parser.')
    # parser.add_argument('--version', help='version')
    # parser.add_argument('--bot_id', help='bot_id')
    # parser.add_argument('--model_dir', help='model_dir', default=MODEL_PATH)
    # args = parser.parse_args()

    config = {"version": '0.1', "bot_id": 'lancome', "output_dir": '/home/iblue/Downloads/faq_bot/chat_model/'}
    path_context = PathContext(config)
    bot = Bot(path_context, {})

    user_id = 'oDljfjhjSKUa4hAeGjFAWehdYtiY'



    async def get_resp():
        while True:
            question = sys.stdin.readline().rstrip()
            intent, response = await bot.get_response(user_id, question)
            # intent = bot.intrepreter.parse(question)
            print(json.dumps(response, ensure_ascii=False))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_resp())
