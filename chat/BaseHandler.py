#!/usr/bin/env python
# coding: utf-8

import json
import logging
from tornado import web
from common.db_util import ConnectManager

# Obtain the global Logger
_logger = logging.getLogger(__name__)


class BaseHandler(web.RequestHandler):

    __db_session = None

    @property
    def db(self):
        if self.__db_session is None:
            self.__db_session = ConnectManager.get_db()
        return self.__db_session

    def on_finish(self):
        if self.__db_session:
            self.__db_session.close()
            self.__db_session = None

    ### forbiden
    def get(self):
        self.write_error(404)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.set_status(404)
            self.write({'code': 404})
            # self.render('404.html', subtitle="404错误", toast="")
        elif status_code == 500:
            self.set_status(500)
            self.write({'code': 500})
            # self.render('500.html', subtitle="500错误", toast="")
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)

    ### wtforms error
    def format(self, form):
        return self.render_string("wterr.html", errors=form.errors)

    ### logging action
    def prepare(self):
        # current = self.get_current_user()
        # action = UserAction(
        #     user_id=(current.user_id if current else 1000),
        #     method=self.request.method,
        #     full_url=self.request.full_url(),
        #     remote_ip=self.request.remote_ip,
        #     user_agent=self.request.headers.get("User-Agent", "")
        # )
        # try:
        #     # self.db.add(action)
        #     self.db.commit()
        # except Exception as e:
        #     self.db.rollback()
        #     _logger.warning(e)
        pass

    def output(self, result):
        self.finish(json.dumps(result, ensure_ascii=False, encoding="utf-8"))

    def set_default_headers(self):
        # self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
