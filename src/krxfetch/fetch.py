import requests

from . import _chrome


class Fetch:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.referer = 'https://data.krx.co.kr'
        self.session.headers.update({
            'User-Agent': _chrome.user_agent()
        })

    def _headers(self, referer: str | None = None) -> dict:
        return {
            'referer': referer or self.referer
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


    def login(self, userid: str, passwd: str) -> bool:
        """
        KRX data.krx.co.kr 로그인 후 세션 쿠키(JSESSIONID)를 갱신합니다.

        로그인 흐름:
          1. GET MDCCOMS001.cmd  → 초기 JSESSIONID 발급
          2. GET login.jsp       → iframe 세션 초기화
          3. POST MDCCOMS001D1.cmd → 실제 로그인
          4. CD011(중복 로그인) → skipDup=Y 추가 후 재전송
        """
        # 1. 로그인 페이지
        login_page = 'https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001.cmd'

        self.session.get(login_page)

        # 2. 로그인 JSP
        login_jsp = 'https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc'
        headers = {
            'Referer': login_page,
        }
        self.session.get(login_jsp, headers=headers)

        # 3. 로그인
        login_url = 'https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd'
        headers = {
            'Referer': login_jsp,
        }
        payload = {
            'mbrNm': '',
            'telNo': '',
            'di': '',
            'certType': '',
            'mbrId': userid,
            'pw': passwd,
        }

        # 로그인 POST
        r = self.session.post(login_url, data=payload, headers=headers)
        json_data = r.json()
        error_code = json_data.get('_error_code')

        # CD011 중복 로그인 처리
        if error_code == 'CD011':
            payload['skipDup'] = 'Y'
            r = self.session.post(login_url, data=payload, headers=headers)
            json_data = r.json()
            error_code = json_data.get('_error_code', '')

        return error_code == 'CD001'  # CD001 = 정상
