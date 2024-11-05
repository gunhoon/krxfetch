import pytest

from krxfetch.fetch import get_json_data
from krxfetch.fetch import download_csv


@pytest.fixture
def payload():
    """[11001] 통계 > 기본 통계 > 지수 > 주가지수 > 전체지수 시세"""

    return {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT00101',
        'locale': 'ko_KR',
        'idxIndMidclssCd': '01',
        'trdDd': '20230602',
        'share': '2',
        'money': '3',
        'csvxls_isNo': 'false'
    }


@pytest.mark.skipif(False, reason='requires http request')
def test_get_json_data(payload):
    data = get_json_data(payload)

    assert data[1]['IDX_NM'] == 'KRX 300'
    assert data[1]['CLSPRC_IDX'] == '1,573.77'


@pytest.mark.skipif(False, reason='requires http request')
def test_download_csv(payload):
    bld = payload.pop('bld')
    payload['name'] = 'fileDown'
    payload['url'] = bld

    csv = download_csv(payload)

    lines = csv.splitlines()
    first = lines[2].split(',')

    assert first[0] == '"KRX 300"'
    assert first[1] == '"1573.77"'
