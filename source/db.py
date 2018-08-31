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
        print(data)
        sql = 'INSERT INTO `stock_neeq_daily_data` (`sse_a_total`, `sse_a_tj`, `sse_b_total`, `sse_b_tj`, `sse_total`, `sse_tj_total`, `szse_total`, `szse_tj`, `neeq_total`, `neeq_tj`, `updated_date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        values = (int(data['sse']['total_a']), int(data['sse']['total_a_tj']), int(data['sse']['total_b']), int(data['sse']['total_b_tj']), int(data['sse']['total_sse']), int(data['sse']['total_sse_tj']), int(data['szse']['total_szse']), int(data['szse']['total_tj']), int(data['neeq']['total']), int(data['neeq']['tj']), arrow.now().format('YYYY-MM-DD'))

        try:
            self.cursor.execute(sql, values)
            self.connect.commit()
        except Exception as e:
            print(e)


    def query(self, date):
        """
        查找上一周的数据
        """
        sql = 'SELECT * FROM `stock_neeq_daily_data` WHERE updated_date="%s"' % date
        if self.cursor.execute(sql) > 0:
            result = self.cursor.fetchall()[0]
            print(result)
            data = {}
            data['sse'] = {
                'total_a': result[1],
                'total_a_tj': result[2],
                'total_b': result[3],
                'total_b_tj': result[4],
                'total_sse': result[12],
                'total_sse_tj': result[13],
            }
            data['szse'] = {
                'total_szse': result[5],
                'total_tj': result[6],
            }
            data['neeq'] = {
                'total': result[7],
                'tj': result[8]
            }
            data['kjxjr_date'] = result[10]
            data['kjxjr'] = result[11]

            return data
        else:
            return None

    def query_kjxjr(self, date):
        """
        单独寻找上一月的科技小巨人数据
        """
        sql = 'SELECT kjxjr from `stock_neeq_daily_data` WHERE kjxjr_date="%s"' % date
        if self.cursor.execute(sql) > 0:
            result = self.cursor.fetchall()[0]
            return result[0]
