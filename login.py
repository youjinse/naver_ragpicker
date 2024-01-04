import requests
from bs4 import BeautifulSoup
import rsa
import uuid
from lzstring import LZString

## 출처 : https://blog.naver.com/nkj2001/222722322802

class NaverLogin(requests.Session):
    def __init__(self, NAVER_ID, NAVER_PASS):
        super().__init__()
        self.NAVER_ID = NAVER_ID
        self.NAVER_PASS = NAVER_PASS
        self.session_key = None
        self.key_name = None
        self.dynamic_key = None
        self.public_key = None
        self.encpw = None
        self. header = {
        "User-Agent" : "Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 \
        (KHTML, like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1"
        }

        self.login_url = "https://nid.naver.com/nidlogin.login?mode=form"

    def _get_keys(self):
        url = self.login_url + "&svctype=262144"
        r = self.get(url, headers=self.header)
        bs = BeautifulSoup(r.text, "lxml")
        keys = bs.find("input", {"id": "session_keys"}).attrs.get("value")
        self.session_key, self.key_name, e, N = keys.split(",")
        self.dynamic_key = bs.find("input", {"id": "dynamicKey"}).attrs.get("value")
        self.public_key = rsa.PublicKey(int(e, 16), int(N, 16))

    def _get_encpw(self):
        t = [self.session_key, self.NAVER_ID, self.NAVER_PASS]
        result = ""
        for k in t:
            result += "".join([chr(len(k)) + k])
        encode_result = result.encode()
        self.encpw = rsa.encrypt(encode_result, self.public_key).hex()

    def login(self):
        self._get_keys()
        self._get_encpw()
        
        bvsd_uuid = str(uuid.uuid4())
        encData = str({
            "a": f"{bvsd_uuid}-4",
            "b": "1.3.4",
            "d": [{
                    "i": "id",
                    "b": {
                        "a": ["0", self.NAVER_ID]
                    },
                    "d": self.NAVER_ID,
                    "e": "false",
                    "f": "false"
                },
                {
                    "i": self.NAVER_PASS,
                    "e": "true",
                    "f": "false"
                }],
            "h": "1f",
            "i":{"a": "Mozilla/5.0"}
        })

        bvsd = str({
            "uuid": bvsd_uuid,
            "encData": LZString.compressToEncodedURIComponent(encData.replace("'", '"'))
        })

        params = {
            "dynamicKey" : self.dynamic_key,
            "encpw" : self.encpw,
            "enctp" : "1",
            "svctype" : "1",
            "smart_LEVEL" : "-1",
            "bvsd" : bvsd.replace("'", '"'),
            "encnm" : self.key_name,
            "locale" : "ko_KR",
            "url" : "https://www.naver.com",
        }
        print(params)
        r = self.post(self.login_url, data=params, headers=self.header)
        if r.text.find("location") >= 0:
            return True
        else:
            return False

if __name__ == "__main__":
    from scret import NAVER_ID, NAVER_PASS
    naver = NaverLogin(NAVER_ID, NAVER_PASS)
    if naver.login():
        print("로그인 성공")
    else:
        print("로그인 실패")