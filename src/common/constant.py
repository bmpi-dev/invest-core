#-*- coding:utf-8 -*-
"""
constants

@author: Lucy
@file: const.py
@time: 2019/03/01
"""

import os

class _Const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const(%s) value" % name)
        if not name.isupper():
            raise self.ConstCaseError("Const name %s is not all uppercase" % name)
        self.__dict__[name] = value

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            raise self.ConstError("Can't return const %s, No Existing Key!" % item)

    def __delattr__(self, item):
        if item in self.__dict__:
            raise self.ConstError("Can't unbind const(%s)" % item)
        raise NameError(item)

const = _Const()
const.TS_TOKEN = os.environ['TUSHARE_API_TOKEN']

const.FILE_LOG = '../logs/lm.log'
const.DATE_FORMAT_ONE = '%Y-%m-%d'
const.DATE_FORMAT_TUSHARE = '%Y%m%d'
const.DATE_START = '20050101'
const.MYSQL_CONN = 'mysql+mysqldb://root:123456@127.0.0.1/stock?charset=utf8mb4'
const.CSV_EXTENSION = 'csv'