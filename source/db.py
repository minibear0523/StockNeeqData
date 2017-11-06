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

    def insert(self, data):
        sql = 'INSERT INTO `stock_neeq_daily_data` (`sse_a_total`, `sse_a_tj`, `sse_b_total`, `sse_b_tj`, `szse_total`, `szse_tj`, `neeq_total`, `neeq_tj`, `updated_date`, `kjxjr_date`, `kjxjr`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values = (data['sse']['total_a'], data['sse']['total_a_tj'], data['sse']['total_b'], data['sse']['total_b_tj'], data['szse']['total_szse'], data['szse']['total_tj'], data['neeq']['total'], data['neeq']['tj'], arrow.now.format('YYYY-MM-DD'), data['kjxjr_date'], data['kjxjr'])

        try:
            self.cursor.execute(sql, values)
            self.connect.commit()
        except Exception as e:
            print(e)


    def query(self, date):
        """
        查找上一周的数据
        """
        return None
