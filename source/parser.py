# encoding=utf-8
import pandas as pd
import arrow
import os
import ujson

class Parser(object):
    def __init__(self, files):
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
        解析上交所的4份文件
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
        sse_a_df = pd.read_csv(sse_a_filename, encoding='gbk')
        total_a = sse_a_df[sse_a_df.columns[0]].count()

        sse_b_df = pd.read_csv(sse_b_filename, encoding='gbk')
        total_b = sse_b_df[sse_b_df.columns[0]].count()

        sse_a_tj_df = pd.read_csv(sse_a_tj_filename, encoding='gbk')
        total_a_tj = sse_a_tj_df[sse_a_tj_df.columns[0]].count()

        sse_b_tj_df = pd.read_csv(sse_b_tj_filename, encoding='gbk')
        total_b_tj = sse_b_tj_df[sse_b_tj_df.columns[0]].count()

        return {'total_a': total_a, 'total_b': total_b, 'total_a_tj': total_a_tj, 'total_b_tj': total_b_tj}

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

        return result
