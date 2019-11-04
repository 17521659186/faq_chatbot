#!/usr/bin/env python
# coding:utf-8
import os

from settings.setting import TRAIN_DATA_PATH, MODEL_PATH


class PathContext:
    def __init__(self, config):
        self.config = config
        self.version = config["version"]
        self.bot_id = config["bot_id"]
        self.croups_dir = self.config["croups_dir"] if "croups_dir" in config else TRAIN_DATA_PATH
        self.model_output_dir = self.config["output_dir"] if "output_dir" in config else MODEL_PATH

        self.train_data_path = os.path.join(self.croups_dir, self.bot_id, self.version)
        self.model_output_path = os.path.join(self.model_output_dir, self.bot_id, self.version)
        self.model_output_path_tmp = os.path.join(self.model_output_dir, self.bot_id, self.version) + "_tmp"
        # self.model_output_without_mode = os.path.join(MODEL_PATH, self.version)

        self.entity_list_path = os.path.join(self.model_output_path, "nlu/croups/entities.json")
        self.entity_regex_path = os.path.join(self.model_output_path,"nlu/croups/regex_entities.json")
        self.patterns_intent_path = os.path.join(self.model_output_path, "nlu/croups/patterns_intent.json")
        self.jieba_user_dict_path = os.path.join(self.model_output_path, "nlu/jieba_userdict/dict.txt")
        self.external_feature_path = os.path.join(self.model_output_path, 'nlu/external_feature/model_feature.json')

        self.nlu_train_path = os.path.join(self.train_data_path, "nlu.json")
        self.nlp_tar_file_path = os.path.join(self.train_data_path, "nlp.tar")

        self.nlu_train_yml = os.path.join(self.model_output_path, "nlu/train.yml")

        self.nlu_zh_model_path = "./nlu/zh_model"
        self.nlu_model_output_path = os.path.join(self.model_output_path, "nlu")

        # self.stories_train_path = os.path.join(self.train_data_path, "stories.json")

        self.faq_train_data_path = os.path.join(self.train_data_path, "faq.json")
        self.faq_answer_mapping_path = os.path.join(self.model_output_path, "faq", "answer_mapping_path.json")
        self.faq_question_answers_path = os.path.join(self.model_output_path, "faq", "question_answers.json")
        self.faq_model_output_path = os.path.join(self.model_output_path, "faq")

        self.nlp_stories_path = os.path.join(self.model_output_path, f"{self.bot_id}_nlp/stories.md")
        self.nlp_yaml_path = os.path.join(self.model_output_path, f"{self.bot_id}_nlp/domain.yml")
        self.nlp_model_path = os.path.join(self.model_output_path, f"{self.bot_id}_nlp/train_model")

        # settings
        self.settings_path = os.path.join(self.model_output_path, "setting", "setting.json")
