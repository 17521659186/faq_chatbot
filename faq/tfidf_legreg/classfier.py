#!/usr/bin/env python
# coding:utf-8
import json
import logging
import os
import random
import jieba
from deeppavlov.models.classifiers.logreg_classifier import LogregClassifier
from faq.tfidf_legreg.tfidf_vectorizer import TfIdfVectorizer

_logger = logging.getLogger(__name__)


class TFIDFClassfier():
    def get_tfidf_model_path(self):
        return os.path.abspath(os.path.join(self.path_context.faq_model_output_path, "tfidf"))

    def get_logreg_model_path(self):
        return os.path.abspath(os.path.join(self.path_context.faq_model_output_path, "logreg"))

    def __init__(self, path_context, top_n=1):
        self.path_context = path_context
        self.top_n = top_n
        self.clf = None
        self.vectorizer = None

    def process_croups(self, train_data):

        questions = []
        answers = []
        answers_mapping = {}

        for id, item in enumerate(train_data):
            questions += item["question"]
            answers += [id] * len(item["question"])
            answers_mapping[id] = item["answers"]
        if not os.path.exists(os.path.dirname(self.path_context.faq_answer_mapping_path)):
            os.makedirs(os.path.dirname(self.path_context.faq_answer_mapping_path))

        with open(self.path_context.faq_answer_mapping_path, "w", encoding='utf-8') as f:
            _logger.info("dump answers mapping to %s" % self.path_context.faq_answer_mapping_path)
            json.dump(answers_mapping, f, ensure_ascii=False)

        return questions, answers

    def train(self, train_data):

        def tokenizer(x):
            sent_words = [list(jieba.cut(item)) for item in x]
            x_tokenized = [" ".join(sent) for sent in sent_words]
            return x_tokenized

        x, y = self.process_croups(train_data)

        x_tokenized = [list(jieba.cut(item)) for item in x]

        vectorizer = TfIdfVectorizer(mode='train', save_path=self.get_tfidf_model_path(),
                                     load_path=self.get_tfidf_model_path())
        vectorizer.fit(x_tokenized)
        x_train = vectorizer(x_tokenized)
        y_train = y

        clf = LogregClassifier(mode='train', top_n=self.top_n, c=1000, penalty='l2',
                               save_path=self.get_logreg_model_path(),
                               load_path=self.get_logreg_model_path())
        clf.fit(x_train, y_train)
        vectorizer.save()
        clf.save()

    def load(self):
        clf = LogregClassifier(mode="", top_n=self.top_n, c=1000, penalty='l2', save_path=self.get_logreg_model_path(),
                               load_path=self.get_logreg_model_path())
        vectorizer = TfIdfVectorizer(mode="", load_path=self.get_tfidf_model_path())
        self.clf = clf
        self.vectorizer = vectorizer
        with open(self.path_context.faq_answer_mapping_path, "r", encoding="utf-8") as f:
            self.answers_mapping = json.load(f)
        return self

    @staticmethod
    def load_model_from_disk(path_context, top_n=1):
        model = TFIDFClassfier(path_context, top_n=top_n)
        return model.load()

    def predict(self, bot_id, user_id, question):
        assert self.clf is not None
        assert self.vectorizer is not None
        tokenized_test_questions = list(map(lambda item: list(jieba.cut(item)), [question]))
        test_q_vectorized = self.vectorizer(tokenized_test_questions)
        result = self.clf(test_q_vectorized)
        answers = (random.choice(self.answers_mapping[str(result[0][0][0])]), result[1][0][0])
        return answers

    def publish(self):
        pass


if __name__ == "__main__":
    clf = TFIDFClassfier("./model/tfidf_loreg/tfidf.pkl", "./model/tfidf_loreg/loreg.pkl",
                         "/Users/jeffrey/Downloads/lancome.xls", 3)
    # clf.train()
    clf = clf.load()
    res = clf.predict("我昨天下的订单，今天为什么查不到")
    print(res)
    res = clf.predict("小黑瓶")
    print(res)
    res = clf.predict("肌肤松弛还有皱纹该怎么办")
    print(res)
    res = clf.predict("激活会员要不要钱")
    print(res)
