import argparse
import datetime
import logging

from krxfetch.fetch import get_json_data


def kospi_price(start_dt, end_dt):
    """[11003] 통계 > 기본 통계 > 지수 > 주가지수 > 개별지수 시세 추이

    :param start_dt: datetime.datetime
    :param end_dt: datetime.datetime
    :return: list
    """
    payload = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT00301',
        'locale': 'ko_KR',
        'tboxindIdx_finder_equidx0_0': '코스피',
        'indIdx': '1',
        'indIdx2': '001',
        'codeNmindIdx_finder_equidx0_0': '코스피',
        'param1indIdx_finder_equidx0_0': '',
        'strtDd': start_dt.strftime('%Y%m%d'),
        'endDd': end_dt.strftime('%Y%m%d'),
        'share': '2',
        'money': '3',
        'csvxls_isNo': 'false'
    }
    logging.info(payload)

    data = get_json_data(payload)
    trading_date = [item['TRD_DD'] for item in data]

    return trading_date


def main(year):
    """main function

    :param year: int
    :return: None
    """
    start_dt = datetime.datetime(year, 1, 1)
    end_dt = datetime.datetime(year, 12, 31)

    trading_date = kospi_price(start_dt, end_dt)
    logging.info(trading_date)

    trading_date = set(trading_date)

    while start_dt <= end_dt:
        if start_dt.weekday() < 5:  # weekday
            # 평일인데 trading date가 아닌 경우는 공휴일
            if start_dt.strftime('%Y/%m/%d') not in trading_date:
                print(start_dt.strftime('%Y-%m-%d'))
        else:  # weekend
            # 주말인데 trading date인 경우는 ERROR
            if start_dt.strftime('%Y/%m/%d') in trading_date:
                logging.error(start_dt)

        start_dt += datetime.timedelta(days=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('year')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(args)

    main(int(args.year))
