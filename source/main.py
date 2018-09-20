# encoding=utf-8
from fetcher import Fetcher
from parser import Parser
from report import Report
from db import DB
import arrow


def begin():
    r = Report()
    try:
        f = Fetcher()
        fetch_result = f.fetch(kjxjr=False)
        p = Parser()
        parse_result = p.parse()

        db = DB()
        db.insert(parse_result)

        today = arrow.now()
        if today.format('dddd') == 'Friday':
            to_addr = [('zhanglei@jixiang2003.com', '张磊'), ('zhangyongquan@jixiang2003.com', '张永泉')]
            r.send_report(to_addr=to_addr)
        else:
            to_addr = [('zhanglei@jixiang2003.com', '张磊'), ]
            r.send_report(to_addr=to_addr)
    except Exception as e:
        print(e)
        r.send_exception()


if __name__ == '__main__':
    begin()
