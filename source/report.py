# encoding=utf-8
from envelopes import Envelope
import ujson
from settings import *
import arrow


class Report(object):
    """
    生成报告, 发送邮件
    """
    def __init__(self, data, files):
        self.data = data
        self.report = None
        self.subject = None
        self.files = files
        self.date = arrow.now()
        self._form_report()
        # self.db = None

    def _form_report(self):
        """
        生成邮件格式的报告, 需要从数据库拿到对应周首日的数据
        """
        # start_date = self.date.shift(days=-5).format('YYYY_MM_DD')
        # start_day_data = self.db.query(start_date)
        # if start_day_data:
        #     self.subject = '沪深股市及新三板数据周报: %s至%s' % (start_date, self.date.format('YYYY_MM_DD'))
        #
        # else:
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
        self.report += '新三板共计挂牌 %s 家企业，其中天津地区挂牌 %s 家企业' % (total_neeq, total_neeq_tj)

    def send_report(self):
        """
        通过邮箱发送报告
        """
        from_addr = ('zhanglei@jixiang2003.com', '张磊')
        to_addr = MAIL_TO_ADDR
        subject = self.subject
        text_body = self.report

        client = Envelope(
            from_addr=from_addr,
            to_addr=to_addr,
            subject=subject,
            text_body=text_body
        )

        client.send(MAIL_SERVER, login=MAIL_LOGIN, password=MAIL_PASSWD, tls=False)
