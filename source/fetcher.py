# encoding=utf-8
#
# Using Selenium to download sse and szse stock list company data.
#
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import ujson
import arrow
from lxml import etree
from urllib.parse import urljoin
import re
from pyvirtualdisplay import Display


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


class Fetcher(object):
    """
    从沪深两市以及新三板的网站上下载对应的统计文件.
    """
    def __init__(self):
        self.driver = None
        self.wait = None
        self.date = arrow.now().format('YYYY_MM_DD')
        self.filepath = './data/%s' % self.date

    def _init_driver(self):
        """
        初始化相关的driver和相关文件系统
        """
        # 创建文件夹
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        # Chrome Options: 确定文件下载的地址
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"')
        options.add_argument('accept-language="zh-CN"')
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': self.filepath
        }
        options.add_experimental_option('prefs', prefs)
        # Selenium相关的初始化
        self.driver = webdriver.Chrome('/home/zhanglei/Work/chromedriver', chrome_options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def close_driver(self):
        if self.driver is not None:
            self.driver.close()
        if self.display is not None:
            self.display.stop()

    def _open(self, url):
        if self.driver is None:
            self._init_driver()
        self.driver.get(url)

    def download_sse(self):
        """
        下载上交所数据, 分为A/B股的全量和天津地区数据
        http://www.sse.com.cn/market/stockdata/statistic/
        """
        # 1. 打开上交所上市公司URL, 默认是A股全量数据
        self._open(SSE_DOWNLOAD_URL)
        time.sleep(1.5)

        # 2.1 下载A股全量数据
        print('下载上交所A股全量数据')
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(1.5)

        # 2.2 下载B股全量数据
        print('下载上交所B股全量数据')
        b_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[2]/a')))
        assert b_btn.text.strip() == '上市B股'
        b_btn.click()
        time.sleep(1.5)
        self.driver.implicitly_wait(5)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(1.5)

        # 3. 选择天津地区下拉框
        print('切换天津地区数据')
        self.driver.find_element_by_xpath('//button[contains(@class, "ms-choice")]').click()
        tj_btn = self.driver.find_element_by_xpath('//div[@class="ms-drop ms-bottom"]/ul/li/label/input[@value="19"]')
        self.driver.execute_script('arguments[0].focus();', tj_btn)
        ActionChains(self.driver).move_to_element(tj_btn).click().perform()
        time.sleep(1.5)
        self.driver.find_element_by_id('btnQuery').click()
        self.driver.implicitly_wait(5)
        time.sleep(1.5)

        # 4.1 下载B股天津数据
        print('下载上交所B股天津数据')
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(1.5)

        # 4.2 下载A股天津数据
        print('下载上交所A股天津数据')
        a_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tabbable"]/ul/li[1]/a')))
        assert a_btn.text.strip() == '上市A股'
        a_btn.click()
        time.sleep(1.5)
        self.driver.implicitly_wait(5)
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="download-export"]')))
        download_btn.click()
        time.sleep(1.5)


    def download_szse(self):
        """
        下载深交所数据
        """
        self._open(SZSE_DOWNLOAD_URL)
        print('下载深交所全量数据')
        download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//table[contains(@class, "cls-title-table-common")]/tbody/tr/td[@align="right"]/a')))
        download_btn.click()
        time.sleep(15)

    def download_neeq(self):
        """
        通过新三板的JSON API接口请求数据
        """
        self.close_driver()
        total_neeq = 0
        tj_neeq = 0

        print('请求新三板全量数据统计')
        total_url = NEEQ_DATA_URL % int(time.time() * 1000)
        req = requests.get(total_url, headers=headers)
        if req.status_code == 200:
            html = req.text[5:-1]
            data = ujson.loads(html)[0]
            total_neeq = data['totalElements']
        else:
            print('请求新三板挂牌公司总数据量失败')

        print('请求新三板天津地区数据统计')
        tj_url = TJ_NEEQ_DATA_URL + str(int(time.time() * 1000))
        req = requests.get(tj_url, headers=headers)
        if req.status_code == 200:
            html = req.text[5:-1]
            data = ujson.loads(html)[0]
            tj_neeq = data['totalElements']
        else:
            print('请求新三板天津地区数据统计失败')

        return total_neeq, tj_neeq

    def download_kjxjr(self):
        """
        下载科技小巨人, 请求页面, 进行解析, 判断是否更新
        """
        h = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Host': 'www.tstc.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }
        url = 'http://www.tstc.gov.cn/zhengwugongkai/zxgz/kjxzxqy/gzdt/'
        req = requests.get(url, headers=h)
        tree = etree.HTML(req.content)

        newest_url = tree.xpath('//div[@class="sub_sameconrcc"]/ul/li[1]/a/@href')[0].strip()
        newest_title = tree.xpath('//div[@class="sub_sameconrcc"]/ul/li[1]/a/text()')[0].strip()

        title_pattern = r'^全市(20[1-9][0-9])年1\-(1?[0-9])月份科技型企业认定情况通报$'
        newest_date = None
        g = re.match(title_pattern, newest_title)
        if g:
            newest_date = '%s_%s' % (g.groups()[0], g.groups()[1])
        else:
            newest_date = newest_title

        req = requests.get(urljoin(url, newest_url), headers=h)
        tree = etree.HTML(req.text)
        data = tree.xpath('//table[@class="MsoNormalTable"][1]/tbody/tr[3]/td[6]/p/b/span/text()')[0].strip()
        return newest_date, data


    def fetch(self, sse=True, szse=True, neeq=True, kjxjr=True):
        """
        需要进一步解耦合,将parser与fetcher的result分离, parser可以直接读取./data/中的文件目录,而不是通过fetcher的结果传入
        将没有文件的新三板和科技小巨人保存到JSON文件或者csv文件中,便于parser解耦合之后也能找到对应数据
        """
        result = {}
        if sse == True:
            self.download_sse()
            # 文件重命名
            sse_a_filename_origin = './data/%s/A股' % self.date
            sse_b_filename_origin = './data/%s/B股' % self.date
            sse_a_filename_dist = './data/%s/SSE_A.csv' % self.date
            sse_b_filename_dist = './data/%s/SSE_B.csv' % self.date
            if os.path.exists(sse_a_filename_origin + '.csv'):
                os.rename(sse_a_filename_origin + '.csv', sse_a_filename_dist)
            else:
                os.rename(sse_a_filename_origin + '.xls', sse_a_filename_dist)
            if os.path.exists(sse_b_filename_origin + '.csv'):
                os.rename(sse_b_filename_origin + '.csv', sse_b_filename_dist)
            else:
                os.rename(sse_b_filename_origin + '.xls', sse_b_filename_dist)
            sse_a_tj_filename = './data/%s/A股 (1)' % self.date
            sse_b_tj_filename = './data/%s/B股 (1)' % self.date
            sse_a_tj_filename_dist = './data/%s/SSE_A_TJ.csv' % self.date
            sse_b_tj_filename_dist = './data/%s/SSE_B_TJ.csv' % self.date
            if os.path.exists(sse_a_tj_filename + '.csv'):
                os.rename(sse_a_tj_filename + '.csv', sse_a_tj_filename_dist)
            else:
                os.rename(sse_a_tj_filename + '.xls', sse_a_tj_filename_dist)
            if os.path.exists(sse_b_tj_filename + '.csv'):
                os.rename(sse_b_tj_filename + '.csv', sse_b_tj_filename_dist)
            else:
                os.rename(sse_b_tj_filename + '.xls', sse_b_tj_filename_dist)

            result['sse'] = {
                'a': sse_a_filename_dist,
                'b': sse_b_filename_dist,
                'tj_a': sse_a_tj_filename_dist,
                'tj_b': sse_b_tj_filename_dist
            }

        if szse == True:
            self.download_szse()
            szse_filename_origin = './data/%s/上市公司列表.xlsx' % self.date
            szse_filename_dist = './data/%s/SZSE.xlsx' % self.date
            os.rename(szse_filename_origin, szse_filename_dist)
            result['szse'] = szse_filename_dist

        if neeq == True:
            total_neeq, tj_neeq = self.download_neeq()
            result['total_neeq'] = total_neeq
            result['tj_neeq'] = tj_neeq

        if kjxjr == True:
            result['kjxjr_date'], result['kjxjr'] = self.download_kjxjr()

        # 将result直接写进文件中,parser读取文件,实现解耦合
        with open(os.path.join(self.filepath, 'result.json'), 'w') as f:
            ujson.dump(result, f)

        return result
