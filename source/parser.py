# encoding=utf-8
import pandas as pd
import arrow
import os
import ujson

class Parser(object):
    def __init__(self, files=None):
        self.date = arrow.now().format('YYYY_MM_DD')
        self.filepath = './data/%s' % self.date
        self.files = None
        if files:
            self.files = files
        else:
            with open(os.path.join(self.filepath, 'result.json'), 'r') as f:
                self.files = ujson.load(f)

    def parse_sse(self):
        """
        重构解析上交所数据, 对同时在A | B上市的企业进行去重
        """
        sse_a_filename = None
        sse_b_filename = None
        sse_a_tj_filename = None
        sse_b_tj_filename = None
        if 'sse' not in self.files:
            sse_a_filename = os.path.join(self.filepath, 'SSE_A.csv')
            sse_b_filename = os.path.join(self.filepath, 'SSE_B.csv')
            sse_a_tj_filename = os.path.join(self.filepath, 'SSE_A_TJ.csv')
            sse_b_tj_filename = os.path.join(self.filepath, 'SSE_B_TJ.csv')
        else:
            sse_a_filename = self.files['sse']['a']
            sse_b_filename = self.files['sse']['b']
            sse_a_tj_filename = self.files['sse']['tj_a']
            sse_b_tj_filename = self.files['sse']['tj_b']
        # 读取数据表
        sse_a_df = pd.read_table(sse_a_filename, encoding='gbk')
        sse_b_df = pd.read_table(sse_b_filename, encoding='gbk')
        sse_a_tj = pd.read_table(sse_a_tj_filename, encoding='gbk')
        sse_b_tj = pd.read_table(sse_b_tj_filename, encoding='gbk')

        # 提取企业名称, 便于统计和去重
        sse_a_titles = sse_a_df['公司简称 '].tolist()
        sse_b_titles = sse_b_df['公司简称 '].tolist()
        sse_a_tj_titles = sse_a_tj['公司简称 '].tolist()
        sse_b_tj_titles = sse_b_tj['公司简称 '].tolist()

        # 进行统计和去重
        total_sse = list(set(sse_a_titles + sse_b_titles))
        total_sse_tj = list(set(sse_a_tj_titles + sse_b_tj_titles))
        return {
            'total_a': len(sse_a_titles),
            'total_b': len(sse_b_titles),
            'total_a_tj': len(sse_a_tj_titles),
            'total_b_tj': len(sse_b_tj_titles),
            'total_sse': len(total_sse),
            'total_sse_tj': len(total_sse_tj)
        }

    def parse_szse(self):
        szse_filename = None
        if 'szse' not in self.files:
            szse_filename = os.path.join(self.filepath, 'SZSE.xlsx')
        else:
            szse_filename = self.files['szse']
        szse_df = pd.read_excel(szse_filename)
        total_count = szse_df['公司代码'].count()
        total_tj = szse_df[szse_df['省    份'] == '天津']['公司代码'].count()
        return {'total_szse': total_count, 'total_tj': total_tj}

    def parse(self):
        result = {}

        sse_result = self.parse_sse()
        if sse_result is not None:
            result['sse'] = sse_result

        szse_result = self.parse_szse()
        if szse_result is not None:
            result['szse'] = szse_result

        if 'total_neeq' in self.files:
            result['neeq'] = {
                'total': self.files['total_neeq'],
                'tj': self.files['tj_neeq']
            }

        if 'kjxjr' in self.files:
            result['kjxjr'] = self.files['kjxjr']
            result['kjxjr_date'] = self.files['kjxjr_date']

        return result
