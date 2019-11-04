#!/usr/bin/env python
# coding:utf-8
import asyncio
import concurrent
import hashlib
import json
import logging
import os
import shutil
import traceback

from faq.tfidf_legreg.classfier import TFIDFClassfier
from train.context import PathContext
from train.reader import TrainDataReader

_logger = logging.getLogger("root")


class FAQTrainTask():
    def __init__(self, config, path_context, settings={}):
        self.config = config
        self.path_context = path_context
        self.settings = settings

    def run(self):
        # if os.path.exists(self.path_context.faq_train_data_path):
        try:
            self.train_faq_model()
        except Exception as e:
            _logger.error("Train FAQ error. Version %s" % self.config["version"])
            _logger.error(traceback.format_exc())
            return {"status": "fail", "name": "faq"}

    def train_faq_model(self):
        train_data = None
        if os.path.exists(self.path_context.faq_train_data_path):
            with open(self.path_context.faq_train_data_path, "r",encoding='utf-8') as f:
                train_data = json.load(f)
        if not train_data:
            _logger.info("FAQ is empty. Version {}".format(self.config["version"]))
            return

        train_data = train_data if train_data  else []
        if not os.path.exists(self.path_context.faq_model_output_path):
            os.makedirs(self.path_context.faq_model_output_path)

        # anyq = AnyQModule(config={"config": self.config, "path_context": self.path_context})
        # anyq.train(train_data)

        clf = TFIDFClassfier(self.path_context)
        clf.train(train_data)
        return {"status": "success", "name": "faq"}


def file_md5(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
            return md5


def move_train_files(from_path, to_path):
    if not os.path.exists(to_path):
        shutil.move(from_path, to_path)
    else:
        for item in os.listdir(from_path):
            dist_item_path = os.path.join(to_path, item)
            from_item_path = os.path.join(from_path, item)
            if os.path.exists(dist_item_path):
                shutil.rmtree(dist_item_path)
            shutil.move(from_item_path, dist_item_path)


async def train(config, loop):
    path_context = PathContext(config)
    dump_model(path_context)
    result = []
    train_success = True

    reader = TrainDataReader(path_context)
    if reader:
        training_data, settings = reader.read_from_json()

    tasks = []

    _logger.info("trian faq model")
    # train faq model
    faq_task = FAQTrainTask(config, path_context, settings if settings else {})
    tasks.append(faq_task.run)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for task in tasks:
            task_result = await loop.run_in_executor(pool, task)
            result.append(task_result)

    for msg in result:
        if msg:
            if msg["status"] == "fail":
                train_success = False
                _logger.error("Train Model error. Version {version}. Module {name}".format(version=config["version"],
                                                                                           name=msg["name"]))
                break
    clean_model(path_context, train_success)
    return train_success


def dump_model(path_context):
    if os.path.exists(path_context.model_output_path):
        _logger.info("Copy model to tmp. From {} to {}".format(path_context.model_output_path,
                                                               path_context.model_output_path_tmp))
        shutil.move(path_context.model_output_path, path_context.model_output_path_tmp)


def clean_model(path_context, train_succes=True):
    if train_succes:
        if os.path.exists(path_context.model_output_path_tmp):
            shutil.rmtree(path_context.model_output_path_tmp)
    else:
        if os.path.exists(path_context.model_output_path):
            shutil.rmtree(path_context.model_output_path)
        if os.path.exists(path_context.model_output_path_tmp):
            shutil.move(path_context.model_output_path_tmp, path_context.model_output_path)


if __name__ == '__main__':
    config = {
        "version": "0.1",
        'bot_id': 'lancome'
    }


    async def train_model(loop):
        await train(config, loop)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(train_model(loop))
