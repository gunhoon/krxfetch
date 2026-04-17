import os

import requests

from . import _chrome


class Fetch:
    def __init__(self):
        self.session = requests.Session()
        self.referer = 'https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201'
        self.session.headers.update({
            'User-Agent': _chrome.user_agent()
        })

    def _headers(self, referer: str | None = None) -> dict:
        return {
            'Referer': referer or self.referer
        }

    def get_json_data(self, payload: dict) -> list[dict]:
        headers = self._headers()

        url = 'https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

        r = self.session.post(url=url, headers=headers, data=payload)
        json_data = r.json()

        keys = list(json_data)
        k = keys[1] if keys[0] == 'CURRENT_DATETIME' else keys[0]

        if k != 'output' and k != 'OutBlock_1' and k != 'block1':
            raise NotImplementedError(k)

        return json_data[k]

    def download_csv(self, payload: dict) -> str:
        headers = self._headers()

        # 1. Generate OTP
        otp_url = 'https://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

        r = self.session.post(url=otp_url, headers=headers, data=payload)
        otp = {
            'code': r.text
        }

        # 2. Download CSV
        url = 'https://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'

        r = self.session.post(url=url, headers=headers, data=otp)
        csv = r.content.decode(encoding='euc_kr')

        return csv

    def login(self, username: str | None = None, password: str | None = None) -> bool:
        # 1. LOAD username, password
        if not username:
            username = os.environ.get('KRX_ID')
        if not password:
            password = os.environ.get('KRX_PW')

        if not username or not password:
            print('Error: No username or password provided')
            return False

        # 2. GET login page
        page_url = 'https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001.cmd'

        r = self.session.get(url=page_url)
        # print(r.headers)
        # print(r.cookies)
        # print(self.session.headers)
        # print(self.session.cookies)
        if r.status_code != 200:
            print(r.status_code)
            return False

        # 3. GET iframe
        iframe_url = 'https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc'
        headers = self._headers(referer=page_url)

        r = self.session.get(iframe_url, headers=headers)
        # print(r.headers)
        # print(r.cookies)
        # print(self.session.headers)
        # print(self.session.cookies)
        if r.status_code != 200:
            print(r.status_code)
            return False

        # 4. POST login
        login_url = 'https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd'
        headers = self._headers(referer=iframe_url)
        payload = {
            'mbrNm': '',
            'telNo': '',
            'di': '',
            'certType': '',
            'mbrId': username,
            'pw': password
        }

        r = self.session.post(url=login_url, headers=headers, data=payload)
        json_data = r.json()
        print(json_data)
        error_code = json_data.get('_error_code')

        # 5. CD011: 중복 로그인
        if error_code == 'CD011':
            payload['skipDup'] = 'Y'
            r = self.session.post(login_url, headers=headers, data=payload)
            json_data = r.json()
            print(json_data)
            error_code = json_data.get('_error_code')

        if error_code != 'CD001': # CD001 = 정상
            print(json_data)
            return False

        return True
