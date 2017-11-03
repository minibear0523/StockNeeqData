# encoding=utf-8
import pymysql
import arrow


class DB(object):
    """
    mysql保存对应的每日数据
    """
    def __init__(self):
        self.connect = pymysql.connect(
            host='localhost',
            db='jixiang_company',
            user='zhanglei',
            passwd='Bear900523',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def __del__(self):
        self.connect.close()


    def insert(self, data):
        pass

    def query(self, date):
        """
        查找上一周的数据
        """
        pass
