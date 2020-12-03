# -*- coding:utf-8 -*-
"""
个股层面信息
包括个股列表、价格、指标、利润信息

@author: Lucy
@file: stock.py
@time: 2019/03/03
"""

import time
import pandas as pd
import xlrd
from core.market import MarketInfo
import util.dateutil as dtu
import util.dbutil as dbu
import util.tsutil as tsu

enum_to_int = {
    "list_status": {"L": 0, "D": 1, "P": 2},  # 上市状态
    "is_hs": {"N": 0, "H": 1, "S": 2}  # 是否沪深港通
}

class StockInfo:

    def __init__(self, market_info):
        self._market_info = market_info

    def save_stock_list(self):
        """
        保存上市股票信息
        该接口只有上市股票数据，没有退市股票数据
        保留旧记录，增加新记录
        """
        table_stock_basic = 'stock_basic'
        try:
            # ts_code to drop
            stock_exist = dbu.read_df("SELECT ts_code FROM %s" % table_stock_basic)
            ts_code_drop = stock_exist['ts_code']
            # load data from tushare
            stock_list = tsu.query_stock_list()
            # difference set
            flag = stock_list['ts_code'].isin(ts_code_drop)
            diff_flag = [not f for f in flag]
            stock_list = stock_list[diff_flag]
            # type conversion
            stock_list.replace(to_replace=enum_to_int, inplace=True)
            stock_list['list_date'] = dtu.tsformat_col_to_datetime(stock_list['list_date'])
            stock_list['delist_date'] = dtu.tsformat_col_to_datetime(stock_list['delist_date'])
            # insert new records
            dbu.save_df(stock_list, table_stock_basic)
            print("Successfully load stock list: %d" % stock_list.shape[0])
        except Exception as e:
            print(e)

    def _append_daily_info(self, trade_date):
        """
        保存每日行情数据和指标
        :param trade_date: str
            example: 20190101
        """
        trade_date_tmp = trade_date
        table_stock_price = 'stock_price'
        sql_stock_price = "SELECT count(1) AS count FROM stock_price WHERE trade_date='%s'" % trade_date_tmp
        try:
            # check if data exists
            res = dbu.read_df(sql_stock_price)
            count = res['count'].iloc[0]
            if count > 0:
                print("Daily price exists: %s" % trade_date)
                return
            # load date
            price_daily = tsu.query_stock_price_daily(trade_date)
            basic_daily = tsu.query_stock_basic_daily(trade_date)
            info_daily = pd.merge(price_daily, basic_daily, how='left', on=['ts_code', 'trade_date'])
            # save
            dbu.save_df(info_daily, table_stock_price)
            print("Successful load daily price: %s" % trade_date)
            time.sleep(2)
        except Exception as e:
            print("Failed to load daily price: %s" % trade_date)
            raise e

    def save_daily_info(self, start_date, end_date):
        """
        按日保存个股数据
        :param start_date: str
            example:'20180101'
        :param end_date: str
            example:'20180101'
        :param dir: str
            dir path to save daily stock info
        """
        date_iterator = start_date
        trade_date_dict = self._market_info.all_open_date(start_date, end_date)
        frames = []
        while int(date_iterator) <= int(end_date):
            is_open = trade_date_dict.get(date_iterator, 0)
            if is_open == 0:
                print("Not a trade date: %s" % date_iterator)
            else:
                self._append_daily_info(date_iterator)
            date_iterator = dtu.datetime_to_tsformat(dtu.get_next_day(date_iterator))
        if len(frames) == 0:
            return

    def _get_stock_profit(self, stock_code, start_date, end_date):
        """
        按个股保存利润数据
        :param stock_code: str
        :param start_date: str
        :param end_date: str
        """
        try:
            # stock profit exit
            stock_profit = tsu.query_stock_profit(stock_code, start_date, end_date)
            time.sleep(2)
            return stock_profit
        except Exception as e:
            print("Failed to load stock profit: %s" % stock_code)
            raise e

    def save_stock_profit(self, start_date, end_date):
        """
        按个股保存利润数据
        个股列表来自数据库
        :param start_date: str
            如'20181201'
        :param end_date: str
            如'20181201'
        """
        start_date_tmp = dtu.tsformat_to_datetime(start_date)
        start_date_tmp = dtu.datetime_to_dbformat(start_date_tmp)
        end_date_tmp = dtu.tsformat_to_datetime(end_date)
        end_date_tmp = dtu.datetime_to_dbformat(end_date_tmp)
        sql_stock_list = 'SELECT DISTINCT ts_code FROM stock_price'
        sql_stock_profit = 'SELECT ann_date, f_ann_date, end_date, report_type, 1 AS flag_col FROM stock_profit ' \
                           'WHERE ts_code=\'%s\' AND ann_date BETWEEN \'' + start_date_tmp + \
                           '\' AND \'' + end_date_tmp + '\''
        table_stock_profit = 'stock_profit'
        try:
            # load stock list
            stock_list = dbu.read_df(sql_stock_list)
            # iterate
            for stock_code in stock_list['ts_code']:
                stock_profit = self._get_stock_profit(stock_code, start_date=start_date, end_date=end_date)
                # insert latest records
                if stock_profit.shape[0] > 0:
                    stock_profit_exist = dbu.read_df(sql_stock_profit % stock_code)
                    if stock_profit_exist.shape[0] > 0:
                        stock_profit_exist['ann_date'] = dtu.datetime_col_to_tsformat(stock_profit_exist['ann_date'])
                        stock_profit_exist['f_ann_date'] = dtu.datetime_col_to_tsformat(
                            stock_profit_exist['f_ann_date'])
                        stock_profit_exist['end_date'] = dtu.datetime_col_to_tsformat(stock_profit_exist['end_date'])
                        stock_profit_exist['report_type'] = stock_profit_exist['report_type'].apply(lambda x: str(x))
                        stock_profit = pd.merge(stock_profit, stock_profit_exist, how='left',
                                                on=['ann_date', 'f_ann_date', 'end_date', 'report_type', 'end_date'])
                        stock_profit = stock_profit[pd.isnull(stock_profit['flag_col'])]
                        stock_profit = stock_profit.drop(['flag_col'], axis=1)
                if stock_profit.shape[0] > 0:
                    # type conversion
                    stock_profit['ann_date'] = dtu.tsformat_col_to_datetime(stock_profit['ann_date'])
                    stock_profit['f_ann_date'] = dtu.tsformat_col_to_datetime(stock_profit['f_ann_date'])
                    stock_profit['end_date'] = dtu.tsformat_col_to_datetime(stock_profit['end_date'])
                    dbu.save_df(stock_profit, table_stock_profit)
                    print("Successfully load stock profit: %s, num: %d" % (stock_code, stock_profit.shape[0]))
                else:
                    print("No stock profit: %s" % stock_code)
        except Exception as e:
            print(e)




