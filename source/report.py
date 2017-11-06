# encoding=utf-8
from envelopes import Envelope
import ujson
from settings import *
import arrow
from db import DB


class Report(object):
    """
    生成报告, 发送邮件
    """
    def __init__(self, data):
        self.data = data
        self.report = None
        self.subject = None
        self.db = DB()
        self.date = arrow.now()
        self._form_report()

    def _form_report(self):
        """
        生成邮件格式的报告, 需要从数据库拿到对应周首日的数据
        """
        if self.date.format('dddd') == 'Friday':
            last_week = self.date.shift(days=-7).format('YYYY-MM-DD')
            last_week_data = self.db.query(date=last_week)
            if last_week_data:
                self.subject = '沪深股市及新三板数据周报: %s至%s' % (last_week, self.date.format('YYYY-MM-DD'))
                self.report = '沪深股市及新三板数据日报: %s\n\n' % self.date.format('YYYY_MM_DD')
                self.report += '上海证券交易所:\n'

                total_a, total_a_tj = self.data['sse']['total_a'], self.data['sse']['total_a_tj']
                self.report += '上交所A股共计上市 %s 家公司; 其中天津地区上市 %s 家公司;\n' % (total_a, total_a_tj)
                self.report += '上交所A股本周增(减) %s 家公司, 其中天津地区增(减) %s 家公司\n\n' % (int(total_a) - last_week_data['sse']['total_a'], int(total_a_tj) - last_week_data['sse']['total_a_tj'])

                total_b, total_b_tj = self.data['sse']['total_b'], self.data['sse']['total_b_tj']
                self.report += '上交所B股共计上市 %s 家公司; 其中天津地区上市 %s 家公司;\n' % (total_b, total_b_tj)
                self.report += '上交所本周增(减) %s 家公司; 其中天津地区增(减) %s 家公司\n\n' % (int(total_b) - last_week_data['sse']['total_b'], int(total_b_tj) - last_week_data['sse']['total_b_tj'])

                self.report += '上交所共计上市 %s 家公司; 其中天津地区共上市 %s 家公司;\n' % (total_a + total_b, total_a_tj + total_b_tj)
                self.report += '上交所本周共计增(减) %s 家公司, 其中天津地区增(减) %s 家\n\n' % (int(total_a) + int(total_b) - last_week_data['sse']['total_a'] - last_week_data['sse']['total_b'], int(total_a_tj) + int(total_b_tj) - last_week_data['sse']['total_a_tj'] - last_week_data['sse']['total_b_tj'])

                self.report += '深圳证券交易所:\n'
                total_szse, total_tj = self.data['szse']['total_szse'], self.data['szse']['total_tj']
                self.report += '深交所主板、中心板块和创业板共计上市 %s 公司; 其中天津地区上市 %s 家公司;\n' % (total_szse, total_tj)
                self.report += '深交所本周共计增(减) %s 家公司, 其中天津地区本周增(减) %s 家;\n\n' % (int(total_szse) - last_week_data['szse']['total_szse'], int(total_tj) - last_week_data['szse']['total_tj'])

                self.report += '沪深两市合计上市 %s 家公司; 其中天津地区上市 %s 家公司\n' % ((total_a + total_b + total_szse), (total_a_tj + total_b_tj + total_tj))
                self.report += '沪深两市本周共计增(减) %s 家公司, 其中天津地区本周增(减) %s 家\n\n' % ((total_a + total_b + total_szse - last_week_data['sse']['total_a'] - last_week_data['sse']['total_b'] - last_week_data['szse']['total_szse']), (total_a_tj + total_b_tj + total_tj - last_week_data['sse']['total_a_tj'] - last_week_data['sse']['total_b_tj'] - last_week_data['szse']['total_tj']))

                self.report += '全国中小企业股份转让系统（新三板）:\n'
                total_neeq, total_neeq_tj = self.data['neeq']['total'], self.data['neeq']['tj']
                self.report += '新三板共计挂牌 %s 家企业; 其中天津地区挂牌 %s 家企业\n' % (total_neeq, total_neeq_tj)
                self.report += '新三板本周增(减) %s 家企业, 其中天津地区增(减) %s 家\n\n' % (total_neeq - last_week_data['neeq']['total'], total_neeq_tj - last_week_data['neeq']['tj'])

                self.report += '天津市科学技术委员会科技小巨人认定情况:\n'
                self.report += '截至 %s, 天津市科学技术委员会总计认定科技小巨人企业 %s 家\n\n' % (self.data['kjxjr_date'], self.data['kjxjr'])
                return

        # 周五发送周报, 平时发送日报
        self.subject = '沪深股市及新三板数据日报: %s' % self.date.format('YYYY_MM_DD')
        self.report = '沪深股市及新三板数据日报: %s\n\n' % self.date.format('YYYY_MM_DD')
        self.report += '上海证券交易所:\n'
        total_a, total_a_tj = self.data['sse']['total_a'], self.data['sse']['total_a_tj']
        self.report += '上交所A股共计上市 %s 家公司，其中天津地区上市 %s 家公司;\n' % (total_a, total_a_tj)
        total_b, total_b_tj = self.data['sse']['total_b'], self.data['sse']['total_b_tj']
        self.report += '上交所B股共计上市 %s 家公司，其中天津地区上市 %s 家公司;\n' % (total_b, total_b_tj)
        self.report += '上交所共计上市 %s 家公司，其中天津地区共上市 %s 家公司;\n\n' % (total_a + total_b, total_a_tj + total_b_tj)

        self.report += '深圳证券交易所:\n'
        total_szse, total_tj = self.data['szse']['total_szse'], self.data['szse']['total_tj']
        self.report += '深交所主板、中心板块和创业板共计上市 %s 公司，其中天津地区上市 %s 家公司\n\n' % (total_szse, total_tj)

        self.report += '沪深两市合计上市 %s 家公司，其中天津地区上市 %s 家公司\n\n' % ((total_a + total_b + total_szse), (total_a_tj + total_b_tj + total_tj))

        self.report += '全国中小企业股份转让系统（新三板）:\n'
        total_neeq, total_neeq_tj = self.data['neeq']['total'], self.data['neeq']['tj']
        self.report += '新三板共计挂牌 %s 家企业，其中天津地区挂牌 %s 家企业\n\n' % (total_neeq, total_neeq_tj)

        self.report += '天津市科学技术委员会科技小巨人认定情况:\n'
        self.report += '截至 %s, 天津市科学技术委员会总计认定科技小巨人企业 %s 家\n\n' % (self.data['kjxjr_date'], self.data['kjxjr'])

    def send_report(self, to_addr):
        """
        通过邮箱发送报告
        """
        from_addr = ('zhanglei@jixiang2003.com', '张磊')
        to_addr = to_addr
        subject = self.subject
        text_body = self.report

        client = Envelope(
            from_addr=from_addr,
            to_addr=to_addr,
            subject=subject,
            text_body=text_body
        )

        client.send(MAIL_SERVER, login=MAIL_LOGIN, password=MAIL_PASSWD, tls=False)
