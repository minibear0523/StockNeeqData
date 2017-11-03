# encoding=utf-8
import pandas as pd
import arrow

class Parser(object):
    def __init__(self, files):
        self.date = arrow.now().format('YYYY_MM_DD')
        self.filepath = './data/%s' % self.date
        self.files = files

    def parse_sse(self):
        """
        解析上交所的4份文件
        """
        if 'sse' not in self.files:
            return None
        sse_a_df = pd.read_csv(self.files['sse']['a'], encoding='gbk')
        total_a = sse_a_df[sse_a_df.columns[0]].count()

        sse_b_df = pd.read_csv(self.files['sse']['b'], encoding='gbk')
        total_b = sse_b_df[sse_b_df.columns[0]].count()

        sse_a_tj_df = pd.read_csv(self.files['sse']['tj_a'], encoding='gbk')
        total_a_tj = sse_a_tj_df[sse_a_tj_df.columns[0]].count()

        sse_b_tj_df = pd.read_csv(self.files['sse']['tj_b'], encoding='gbk')
        total_b_tj = sse_b_tj_df[sse_b_tj_df.cloumns[0]].count()

        return {'total_a': total_a, 'total_b': total_b, 'total_a_tj': total_a_tj, 'total_b_tj': total_b_tj}

    def parse_szse(self):
        if 'szse' not in self.files:
            return None
        szse_df = pd.read_csv(self.files['szse'])
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
