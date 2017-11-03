# encoding=utf-8
from fetcher import Fetcher
from parser import Parser
from report import Report


def begin():
    f = Fetcher()
    fetch_result = f.fetch()
    p = Parser(fetch_result)
    parse_result = p.parse()
    r = Report(data=parse_result, files=fetch_result)
    r.send_report()

if __name__ == '__main__':
    begin()
