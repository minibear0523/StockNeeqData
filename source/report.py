# encoding=utf-8
from envelopes import Envelope
import ujson
from settings import *
import arrow
import re
import pandas as pd
from db import DB


class Report(object):
    """
    生成报告, 发送邮件
    """
    def __init__(self):
        self.report = None
        self.subject = None
        self.db = DB()
        self.date = arrow.now()
        self._form_report()

    def _form_report(self):
        """
        直接从数据库读取数据, 导入到pandas生成html代码
        """
        if self.date.format('dddd') == 'Friday':
            # 周五读取当日和上周五的数据
            # 将沪深两市分量和总量以及新三板放在一个表格中, 上交所A,B板一个表格, 科技小巨人一个表格
            today_data = self.db.query(date=self.date.format('YYYY-MM-DD'))
            last_date = self.date.shift(days=-7).format('YYYY-MM-DD')
            last_data = self.db.query(date=last_date)
            print(last_data)
            if last_data['sse']['total_sse'] == 0:
                last_data['sse']['total_sse'] = int(last_data['sse']['total_a']) + int(last_data['sse']['total_b'])
                last_data['sse']['total_sse_tj'] = int(last_data['sse']['total_a_tj']) + int(last_data['sse']['total_b_tj'])
            total_data, sse_data, kjxjr_data = self._parse_weekly_data(today_data, last_data)

            self.report = total_data.to_html(escape=False)
            self.report += '<br>'
            self.report += sse_data.to_html(escape=False)
            self.report += '<br>'
            # self.report += kjxjr_data.to_html(escape=False)
            self.report += '截至%s:' % self.date.format('YYYY-MM-DD')
            self.report += '<br>'
            self.report += '全国上市公司%s家, 其中天津%s家' % (total_data.loc['沪深两市', '本周总量'], total_data.loc['沪深两市', '本周天津地区'])
            self.report += '<br>'
            self.report += '全国新三板挂牌公司%s家, 其中天津%s家' % (total_data.loc['新三板', '本周总量'], total_data.loc['新三板', '本周天津地区'])
            self.report += '<br>'
            self.report += '截止到2018年7月底,天津市科委评定的规模超万亿元科技型企业共计4,386家'

            self.subject = '数据周报: %s至%s' % (last_date, self.date.format('YYYY-MM-DD'))
        else:
            today_data = self.db.query(date=self.date.format('YYYY-MM-DD'))
            df = self._parse_daily_data(today_data)
            self.report = df.to_html(escape=False)
            self.subject = '数据日报: %s' % self.date.format('YYYY-MM-DD')

    def _parse_daily_data(self, today_data):
        """
        解析当日数据
        """
        stock_columns = ['今日总量', '今日天津地区']
        labels = ['上交所A板', '上交所B板', '上交所', '深交所', '沪深两市', '新三板']

        today_sse_a, today_sse_b = today_data['sse']['total_a'], today_data['sse']['total_b']
        today_sse_a_tj, today_sse_b_tj = today_data['sse']['total_a_tj'], today_data['sse']['total_b_tj']
        today_sse = today_data['sse']['total_sse']
        today_sse_tj = today_data['sse']['total_sse_tj']
        today_szse = today_data['szse']['total_szse']
        today_szse_tj = today_data['szse']['total_tj']
        today_neeq = today_data['neeq']['total']
        today_neeq_tj = today_data['neeq']['tj']
        today_kjxjr_date = today_data['kjxjr_date']
        today_kjxjr = today_data['kjxjr']
        data = [
            [today_sse_a, today_sse_a_tj],
            [today_sse_b, today_sse_b_tj],
            [today_sse, today_sse_tj],
            [today_szse, today_szse_tj],
            [today_sse + today_szse, today_sse_tj + today_szse_tj],
            [today_neeq, today_neeq_tj],
            [today_kjxjr_date, today_kjxjr]
        ]

        df = pd.DataFrame(data, columns=stock_columns, index=labels)
        return df


    def _parse_weekly_data(self, today_data, last_data):
        """
        解析本周五和上周五的数据, 返回三个list, 分别为全量数据, 上交所AB板数据和科技小巨人数据
        """
        stock_columns = ['本周总量', '上周总量', '本周总量变化', '本周天津地区', '上周天津地区', '本周天津地区变化']
        kjxjr_columns = ['当前公布月份', '当前公布总量', '上月公布总量', '变化']
        total_labels = ['上交所', '深交所', '沪深两市', '新三板']
        sse_labels = ['上交所A板', '上交所B板', '上交所总量']
        # kjxjr_labels = ['天津市科技小巨人认证企业']

        # 总量表格
        total_data = []
        # 上交所
        today_sse_a, today_sse_b = today_data['sse']['total_a'], today_data['sse']['total_b']
        today_sse_a_tj, today_sse_b_tj = today_data['sse']['total_a_tj'], today_data['sse']['total_b_tj']
        last_sse_a, last_sse_b = last_data['sse']['total_a'],  last_data['sse']['total_b']
        last_sse_a_tj, last_sse_b_tj = last_data['sse']['total_a_tj'], last_data['sse']['total_b_tj']


        today_sse = today_data['sse']['total_sse']
        last_sse = last_data['sse']['total_sse']
        today_sse_tj = today_data['sse']['total_sse_tj']
        last_sse_tj = last_data['sse']['total_sse_tj']
        total_data.append([today_sse, last_sse, today_sse - last_sse, today_sse_tj, last_sse_tj, today_sse_tj - last_sse_tj])
        # 深交所
        today_szse = today_data['szse']['total_szse']
        last_szse = last_data['szse']['total_szse']
        today_szse_tj = today_data['szse']['total_tj']
        last_szse_tj = last_data['szse']['total_tj']
        total_data.append([today_szse, last_szse, today_szse - last_szse, today_szse_tj, last_szse_tj, today_szse_tj - last_szse_tj])
        # 沪深两市
        total_data.append([today_sse + today_szse, last_sse + last_szse, today_sse + today_szse - last_sse - last_szse, today_sse_tj + today_szse_tj, last_sse_tj + last_szse_tj, today_sse_tj + today_szse_tj - last_sse_tj - last_szse_tj])
        # 新三板
        today_neeq = today_data['neeq']['total']
        last_neeq = last_data['neeq']['total']
        today_neeq_tj = today_data['neeq']['tj']
        last_neeq_tj = last_data['neeq']['tj']
        total_data.append([today_neeq, last_neeq, today_neeq - last_neeq, today_neeq_tj, last_neeq_tj, today_neeq_tj - last_neeq_tj])

        today_df = pd.DataFrame(total_data, columns=stock_columns, index=total_labels)

        # 上交所AB板
        sse_data = [
            [today_sse_a, last_sse_a, today_sse_a - last_sse_a, today_sse_a_tj, last_sse_a_tj, today_sse_a_tj - last_sse_a_tj],
            [today_sse_b, last_sse_b, today_sse_b - last_sse_b, today_sse_b_tj, last_sse_b_tj, today_sse_b_tj - last_sse_b_tj],
            [today_sse, last_sse, today_sse - last_sse, today_sse_tj, last_sse_tj, today_sse_tj - last_sse_tj]
        ]
        sse_df = pd.DataFrame(sse_data, columns=stock_columns, index=sse_labels)

        # 科技小巨人
        today_kjxjr_date = today_data['kjxjr_date']
        today_kjxjr = today_data['kjxjr']
        last_kjxjr_date = arrow.get(today_kjxjr_date.replace('_', '-')).shift(months=-1).format('YYYY_MM')
        last_kjxjr = self.db.query_kjxjr(date=last_kjxjr_date)
        kjxjr_data = [[today_kjxjr_date.replace('_', '-'), today_kjxjr + last_kjxjr, last_kjxjr, today_kjxjr]]
        kjxjr_df = pd.DataFrame(kjxjr_data, columns=kjxjr_columns, index=kjxjr_labels)

        return today_df, sse_df, None


    def send_report(self, to_addr):
        """
        通过邮箱发送报告
        """
        from_addr = ('zhanglei@jixiang2003.com', '张磊')
        to_addr = to_addr
        subject = self.subject
        html_body = self.report

        client = Envelope(
            from_addr=from_addr,
            to_addr=to_addr,
            subject=subject,
            html_body=html_body
        )

        client.send(MAIL_SERVER, login=MAIL_LOGIN, password=MAIL_PASSWD, tls=False)
