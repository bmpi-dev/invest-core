#-*- coding:utf-8 -*-
"""
@author: Lucy
@file: main.py
@time: 2019/03/01
"""
from core.market import MarketInfo
from core.index import IndexInfo
from core.pe_ttm import PEInfo
from core.stock import StockInfo
import util.tsutil as tsu
from common.constant import const
from datetime import datetime
import os
import logging

mi = MarketInfo()
index_info = IndexInfo(mi)
stock_info = StockInfo(mi)
pe_ttm = PEInfo(mi)

# index_info.save_index_list()
# index_info.save_index_stock_component('20201019', '20201019')
# df = tsu.query_index_component('931186.CSI', '20190101', '20190330')
# print(df.head(5))