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
