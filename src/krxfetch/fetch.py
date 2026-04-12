import requests

from . import _chrome


class Fetch:
    def __init__(self, referer: str | None = None) -> None:
        self.session = requests.Session()
        self.referer = referer
        if self.referer is None:
            self.referer = 'https://data.krx.co.kr/contents/MDC/MDI/outerLoader/index.cmd?menuId=MDC0201'

    def _headers(self) -> dict:
        return {
            'user-agent': _chrome.user_agent(),
            'referer': self.referer
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
