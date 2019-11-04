#!/usr/bin/env python
# coding:utf-8
from sqlalchemy import and_
from sqlalchemy import distinct
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from settings.setting import PARAM_FOR_MYSQL


class ConnectManager:
    _engine = create_engine(PARAM_FOR_MYSQL, encoding="utf-8",
                            poolclass=QueuePool, pool_size=20, pool_recycle=100, pool_timeout=30, pool_pre_ping=True)
    db_maker = sessionmaker(bind=_engine)

    @staticmethod
    def get_db():
        return ConnectManager.db_maker()

    @staticmethod
    def close_db(db):
        if db:
            db.close()


class ProductDBHelper:
    def __init__(self, db=None):
        if db:
            self.db = db
        else:
            self.db = ConnectManager.get_db()

    def close(self):
        if self.db:
            self.db.close()
