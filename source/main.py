# encoding=utf-8
from fetcher import Fetcher
from parser import Parser
from report import Report
from db import DB
import arrow


def begin():
    f = Fetcher()
    fetch_result = f.fetch()
    p = Parser()
    parse_result = p.parse()

    db = DB()
    db.insert(parse_result)

    today = arrow.now()

    if today.format('dddd') == 'Friday':
        r = Report(data=parse_result)
        r.send_report()

if __name__ == '__main__':
    begin()
