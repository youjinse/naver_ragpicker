from login import NaverLogin
from scret import NAVER_ID, NAVER_PASS
from time import sleep
import pickle

def start():
    try:
        with open('naver.histroy', 'rb') as f:
            history_data = pickle.load(f)
    except FileNotFoundError:
        history_data = set()

    naver = NaverLogin(NAVER_ID, NAVER_PASS)
    naver_url = 'https://new-m.pay.naver.com/api/adreward/list?pageSize=200&page=1&category=all&deviceType=pc&from=ad_list&collectionId=benefit&channelId=pay'

    naver.login()
    r = naver.get(naver_url)
    if r.ok:
        # print(r.json())
        data = r.json()
        assert data.get('result')
        assert data['result'].get('ads')

        for item in data['result'].get('ads'):
            # print(item.get('clickRewardAmount'))
            if item.get('clickRewardAmount') is not None:
                print(f"campaignId: {item.get('campaignId')} title: {item.get('title')} clickRewardAmount: {item.get('clickRewardAmount')} viewUrl: {item.get('viewUrl')}")
                # cur.execute(f'select ')
                if item.get('campaignId') in history_data:
                    print('기적립건 스킵')
                    continue
                try:
                    link = naver.get(item.get('viewUrl'))
                    history_data.add(item.get('campaignId'))
                except:
                    print('Check Link')
                    continue

                if link.ok is False:
                    print("적립 실패")
                print(f"적립완료 : {item.get('clickRewardAmount')}")
                sleep(5)

    with open('naver.histroy', 'wb') as f:
        history_data = pickle.dump(history_data, f)

if __name__ == '__main__':
    start()