#!/usr/bin/env python
# coding:utf-8
import asyncio

from settings.setting import TRAIN_DATA_PATH, MODEL_PATH
from train.train_helper import train

if __name__ == '__main__':
    import argparse

    # parser = argparse.ArgumentParser(description='Command parser.')
    # parser.add_argument('--version', help='version')
    # parser.add_argument('--bot_id', help='bot_id')
    # parser.add_argument('--croups_dir', help='croups_dir', default=TRAIN_DATA_PATH)
    # parser.add_argument('--output_dir', help='output_dir', default=MODEL_PATH)
    # args = parser.parse_args()

    config = {"version": '0.1', "bot_id": 'lancome', "croups_dir": '/home/iblue/Downloads/faq_bot/train_data/',
              "output_dir": '/home/iblue/Downloads/faq_bot/chat_model/'}

    async def train_model(loop):
        await train(config,loop)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(train_model(loop))
