# encoding=UTF-8
#
# 自动下载上交所, 深交所和新三板的每日数据, 使用pandas统计
#
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import requests
import ujson
from envelopes import Envelope
import arrow


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Host': 'www.neeq.com.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


SSE_DOWNLOAD_URL = 'http://www.sse.com.cn/assortment/stock/list/share/'
SZSE_DOWNLOAD_URL = 'http://www.szse.cn/main/marketdata/jypz/colist/'
NEEQ_DOWNLOAD_URL = 'http://www.neeq.com.cn/nq/listedcompany.html'
NEEQ_DATA_URL = 'http://www.neeq.com.cn/nqxxController/nqxx.do?page=0&typejb=T&xxzqdm=&xxzrlx=&xxhyzl=&xxssdq=&sortfield=xxzqdm&sorttype=asc&dicXxzbqs=&xxfcbj=&_=%s'
TJ_NEEQ_DATA_URL = 'http://www.neeq.com.cn/nqxxController/nqxx.do?page=0&typejb=T&xxzqdm=&xxzrlx=&xxhyzl=&xxssdq=%25E5%25A4%25A9%25E6%25B4%25A5%25E5%25B8%2582&sortfield=xxzqdm&sorttype=asc&dicXxzbqs=&xxfcbj=&_='


class StockListDownloader(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"')
        options.add_argument('accept-language="zh-CN"')
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': './files'
        }
        options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def close(self):
        self.driver.close()

    def _open(self, url):
        self.driver.get(url)

    def download_sse(self):
        """
        下载上交所上A股和B股名单
        """
        # 下载A股,B股的总名单
        self._open(SSE_DOWNLOAD_URL)
        time.sleep(1)
        a_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[1]/a')))
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(3)

        b_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[2]/a')))
        assert b_btn.text.strip() == '上市B股'
        b_btn.click()
        time.sleep(1)
        self.driver.implicitly_wait(5)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(3)

        # 选择天津地区
        a_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[1]/a')))
        assert a_btn.text.strip() == '上市A股'
        a_btn.click()
        self.driver.implicitly_wait(5)
        self.driver.find_element_by_xpath('//button[contains(@class, "ms-choice")]').click()
        tj_btn = self.driver.find_element_by_xpath('//div[@class="ms-drop ms-bottom"]/ul/li/label/input[@value="19"]')
        self.driver.execute_script('arguments[0].focus();', tj_btn)
        ActionChains(self.driver).move_to_element(tj_btn).click().perform()
        time.sleep(1)
        self.driver.find_element_by_id('btnQuery').click()
        self.driver.implicitly_wait(5)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(3)

        b_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[2]/a')))
        assert b_btn.text.strip() == '上市B股'
        b_btn.click()
        time.sleep(1)
        self.driver.implicitly_wait(5)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()

    def download_szse(self):
        """
        下载深交所全部股票的列表
        """
        self._open(SZSE_DOWNLOAD_URL)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//table[contains(@class, "cls-title-table-common")]/tbody/tr/td[@align="right"]/a')))
        download_btn.click()
        time.sleep(20)

    def download_neeq(self):
        """
        通过JSON URL统计相关NEEQ数据
        """
        total_neeq = 0
        tj_neeq = 0

        total_url = NEEQ_DATA_URL % int(time.time() * 1000)
        req = requests.get(total_url, headers=headers)
        if req.status_code == 200:
            html = req.text[5:-1]
            data = ujson.loads(html)[0]
            total_neeq = data['totalElements']
        else:
            print('抓取新三板总数据请求错误')

        tj_url = TJ_NEEQ_DATA_URL + str(int(time.time() * 1000))
        req = requests.get(tj_url, headers=headers)
        if req.status_code == 200:
            html = req.text[5:-1]
            data = ujson.loads(html)[0]
            tj_neeq = data['totalElements']
        else:
            print('抓取新三板天津总数请求错误')

        return total_neeq, tj_neeq

class DataParser(object):
    """
    使用pandas统计数据
    """
    def parse_szse(self):
        """
        深交所数据较全, 可以通过一个文件, 直接使用pandas读取解析
        """
        filename = './files/上市公司列表.xlsx'
        szse_df = pd.read_excel(filename)
        total_count = szse_df['公司代码'].count()
        total_tj = szse_df[szse_df['省    份'] == '天津']['公司代码'].count()
        return total_count, total_tj

    def parse_sse(self):
        """
        上交所数据是分离的,A股/B股, 天津地区A股/B股
        Pandas对于xls文件的读取支持不是很好, 转为csv之后, 使用gbk编码读取
        """
        sse_a_filename = './files/A股'
        sse_b_filename = './files/B股'

        if os.path.exists(sse_a_filename + '.xls'):
            os.rename(sse_a_filename + '.xls', sse_a_filename + '.csv')
        if os.path.exists(sse_b_filename + '.xls'):
            os.rename(sse_b_filename + '.xls', sse_b_filename + '.csv')
        sse_a_df = pd.read_csv(sse_a_filename + '.csv', encoding='gbk')
        sse_b_df = pd.read_csv(sse_b_filename + '.csv', encoding='gbk')
        total_sse_a = sse_a_df[sse_a_df.columns[0]].count()
        total_sse_b = sse_b_df[sse_b_df.columns[0]].count()

        sse_a_tj_filename = './files/A股 (1)'
        sse_b_tj_filename = './files/B股 (1)'
        if os.path.exists(sse_a_tj_filename + '.xls'):
            os.rename(sse_a_tj_filename + '.xls', sse_a_tj_filename + '.csv')
        if os.path.exists(sse_b_tj_filename + '.xls'):
            os.rename(sse_b_tj_filename + '.xls', sse_b_tj_filename + '.csv')
        tj_sse_a_df = pd.read_csv(sse_a_tj_filename + '.csv', encoding='gbk')
        tj_sse_b_df = pd.read_csv(sse_b_tj_filename + '.csv', encoding='gbk')
        total_sse_a_tj = tj_sse_a_df[tj_sse_a_df.columns[0]].count()
        total_sse_b_tj = tj_sse_b_df[tj_sse_b_df.columns[0]].count()

        return total_sse_a, total_sse_a_tj, total_sse_b, total_sse_b_tj

def send_report(report, files):
    """
    通过邮箱发送每日报告和周报
    """
    from_addr = ('minibear_info@163.com', '张磊')
    to_addr = ('zhanglei@jixiang2003.com', 'Test')
    date = arrow.now().format('YYYY/MM/DD')
    subject = '沪深股市数据日报: %s' % date
    envelope = Envelope(
        from_addr=from_addr,
        to_addr=to_addr,
        subject=subject,
        text_body=report
    )
    for filename in files:
        envelope.add_attachment(filename)

    envelope.send('smtp.163.com', login='minibear_info@163.com', password='elaine1986422', tls=False)

def form_report(data):
    """
    生成报告
    """
    report = '沪深股市数据日报: %s\n' % arrow.now().format('YYYY/MM/DD')
    report += '上海证券交易所:\n'
    report += '上交所A股共计上市 %s 家公司, 其中天津地区上市 %s 家公司;\n' % (data['total_sse_a'], data['total_sse_a_tj'])
    report += '上交所B股共计上市 %s 家公司, 其中天津地区上市 %s 家公司;\n' % (data['total_sse_b'], data['total_sse_b_tj'])
    report += '上交所共计上市 %s 家公司, 其中天津地区上市 %s 家公司;\n\n' % (int(data['total_sse_a']) + int(data['total_sse_b']), int(data['total_sse_a_tj']) + int(data['total_sse_b_tj']))

    report += '深圳证券交易所:\n'
    report += '深交所主板, 中小板块和创业板共计上市 %s 家公司, 其中天津地区上市 %s 家公司\n\n' % (data['total_szse'], data['total_szse_tj'])

    report += '全国中小企业股份转让系统(新三板):\n'
    report += '新三板共计挂牌 %s 家公司, 其中天津公司挂牌 %s 家公司\n\n' % (data['total_neeq'], data['tj_neeq'])

    report += '数据来源:\n上交所(http://www.sse.com.cn)\n深交所(http://www.szse.cn)\n全国中小企业股份转让系统(http://www.neeq.com.cn)\t每日公开统计数据'

    return report

def process_file():
    date = arrow.now().format('YYYY_MM_DD')
    szse_filename_origin = './files/上市公司列表.xlsx'
    szse_filename_dist = './files/深交所上市公司列表_%s.xlsx' % date
    os.rename(szse_filename_origin, szse_filename_dist)

    sse_a_filename_origin = './files/A股'
    sse_b_filename_origin = './files/B股'
    sse_a_filename_dist = './files/SSE_A_%s.csv' % date
    sse_b_filename_dist = './files/SSE_B_%s.csv' % date
    if os.path.exists(sse_a_filename_origin + '.csv'):
        os.rename(sse_a_filename_origin + '.csv', sse_a_filename_dist)
    else:
        os.rename(sse_a_filename_origin + '.xls', sse_a_filename_dist)

    if os.path.exists(sse_b_filename_origin + '.csv'):
        os.rename(sse_b_filename_origin + '.csv', sse_b_filename_dist)
    else:
        os.rename(sse_b_filename_origin + '.xls', sse_b_filename_dist)

    sse_a_tj_filename = './files/A股 (1)'
    sse_b_tj_filename = './files/B股 (1)'
    sse_a_tj_filename_dist = './files/SSE_A_TJ_%s.csv' % date
    sse_b_tj_filename_dist = './files/SSE_B_TJ_%s.csv' % date
    if os.path.exists(sse_a_tj_filename + '.csv'):
        os.rename(sse_a_tj_filename + '.csv', sse_a_tj_filename_dist)
    else:
        os.rename(sse_a_tj_filename + '.xls', sse_a_tj_filename_dist)
    if os.path.exists(sse_b_tj_filename + '.csv'):
        os.rename(sse_b_tj_filename + '.csv', sse_b_tj_filename_dist)
    else:
        os.rename(sse_b_tj_filename + '.xls', sse_b_tj_filename_dist)

    return [szse_filename_dist, sse_a_filename_dist, sse_b_filename_dist, sse_a_tj_filename_dist, sse_b_tj_filename_dist]


if __name__ == '__main__':
    downloader = StockListDownloader()
    print('开始下载上交所数据')
    downloader.download_sse()
    time.sleep(5)
    print('上交所A股和B股数据下载完成')
    print('开始下载深交所数据')
    downloader.download_szse()
    print('深交所全部公司列表数据下载完成')
    downloader.close()
    print('开始下载新三板数据')
    total_neeq, tj_neeq = downloader.download_neeq()
    print('新三板总数: %s, 天津总数: %s' % (total_neeq, tj_neeq))
    # TODO: 下载具体列表, 保存到服务器
    # 分析数据
    parser = DataParser()
    total_szse, total_szse_tj = parser.parse_szse()
    total_sse_a, total_sse_a_tj, total_sse_b, total_sse_b_tj = parser.parse_sse()
    data = {
        'total_sse_a': total_sse_a,
        'total_sse_a_tj': total_sse_a_tj,
        'total_sse_b': total_sse_b,
        'total_sse_b_tj': total_sse_b_tj,
        'total_szse': total_szse,
        'total_szse_tj': total_szse_tj,
        'total_neeq': total_neeq,
        'tj_neeq': tj_neeq
    }
    report = form_report(data)
    files = process_file()
    send_report(report, files)
