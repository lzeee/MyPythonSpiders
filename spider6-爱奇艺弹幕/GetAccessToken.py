import json

import requests


class GetAccessToken:
    def __init__(self):
        # 【修改点1】输入自己在百度AI控制台申请应用后获得的AK和SK
        self.AK = 'A408W0SO0KGeIctWxiZ0tc9l'
        self.SK = 'lGkc02q3oTodSNOxGiV4A4XRSvFrhtW8'

        self.AK = 'ALTpRaFmZ8dOeeFoxjHsQ1zH'
        self.SK = 'rwL0Vvmb10IfmIFn4biOEUEIHtYlOubq'

        self.token_url = 'https://aip.baidubce.com/oauth/2.0/token?'\
            + 'grant_type=client_credentials&client_id='\
            + self.AK + '&client_secret=' \
            + self.SK
        self.headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def get_access_token(self):
        r = requests.get(self.token_url, headers=self.headers)
        if r.text:
            tokenkey = json.loads(r.text)['access_token']
            print('get token success')
            return tokenkey
        else:
            print('get token fail')
            return ''


if __name__ == "__main__":
    A = GetAccessToken().get_access_token()
    print(A)
