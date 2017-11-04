# encoding=utf-8
import pymysql
import arrow
from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DBNAME


class DB(object):
    """
    mysql保存对应的每日数据
    """
    def __init__(self):
        self.connect = pymysql.connect(
            host=MYSQL_HOST,
            db=MYSQL_DBNAME,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWD,
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
        return None
