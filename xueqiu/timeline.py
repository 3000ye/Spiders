import time
import random
import requests
import re
import os
import json
from datetime import datetime

from utils.logger import Logger
logger = Logger(name="XueQiu timeline")


headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "referer": "https://xueqiu.com/"
}

cookie = "cookiesu=771740236235970; Hm_lvt_1db88642e346389874251b5a1eded6e3=1740236236; HMACCOUNT=FA22D531B8DD38C5; device_id=98e60459e4744dc65d7e96f3806fbf04; s=bv11co2fy0; bid=2cf207f1534b00bf635945ffaac73030_m7gbvfmj; snbim_minify=true; remember=1; xq_a_token=345d667ef7e914cfb820b0dd92324df2dfdc3789; xqat=345d667ef7e914cfb820b0dd92324df2dfdc3789; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjUwNTk1NDU3OTEsImlzcyI6InVjIiwiZXhwIjoxNzQyOTU4Njc0LCJjdG0iOjE3NDAzODIwNjE1MzAsImNpZCI6ImQ5ZDBuNEFadXAifQ.hXJrtwC2Q6veA3thWWERQXJH7VqKSH6uoRpWhbUlK1VfPZtb8EdUqU7pwJXiWNT0fSamdnLcJxoMbUNdX7dpmzVZoGQmTdWKVeNhWnvtsN-QiAZZHF9VioZ6GUpKjaBNa2T5DRQ7V1rlraOGz2dX5oGKhh6OegV9y3NaPyyMbkgXGogRADjFRq8wiZb_HChUGFDLDzqrLApssfTzKgvsNAcFYsx_5COOT3JQyovfUirHRFoMWwlNDoR1EeZNfUR7Z_BKE2DhGjxmVye7EsVr4W-QcmXes-dr0oDUR_gXVPkUD7528zSM5kso5686X2nxmouMQoa956e3Creiv6YAUQ; xq_r_token=9c0cb4a4e479edbf86f365e29b60668aa4a884c6; xq_is_login=1; u=5059545791; acw_tc=0b32973a17404023884542723ebd51652a12ad5268aa1a0d58cd3d7f9a1412; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1740402583; ssxmod_itna=YqUhD5AK7IMDkFDXKDHD0W5biQeD=Hhqo5q5Cobs1Dlp3xA5D8D6DQeGTbcs5HWUiSb+e6bCO45DgQBRdvNZ0guLWKL22qF4CSYxiTD4q07Db4GkDAqiOD7LuKDxpq0rD74irDDxD3RxDtD1w=D7ONS0wN07T=2CkNDm+=nDGQ9DiUQxi5ePm0ZDMwZDD3QxB6qxA3nD7tDOwQDbqDump63yqDLRjaONP=DbEpStZWDtqnnYL4V4Ci94I+fKGPGtr4wB7xtt7EiFBxFY7hdBBx5ti+P/7hPbGGp/KYXfH+dYcdGFiD==; ssxmod_itna2=YqUhD5AK7IMDkFDXKDHD0W5biQeD=Hhqo5q5CobsD62tlrmlx055y4itDLCl6qTFdDw1hKGcDYI24qBiw0DxD==="
cookies = dict(re.findall(r'([^=;]+)=([^=;]+)', cookie))


def req_json(uid: int, page: int):
    url = f"https://xueqiu.com/statuses/original/timeline.json?user_id={uid}&page={page}&count=50&md5__1038=n4mx0DBDuiitiQrDsKgqCqGKu%2Fzs%3D3HD97oD"
    logger.info(f"request json => uid = {uid}, page = {page}")

    resp = requests.get(url, cookies=cookies, headers=headers)
    resp.encoding = "utf-8"
    resp = resp.json()

    if "list" not in resp:
        failed.append(uid)
        time.sleep(60)
        logger.error(f"request json failed => uid = {uid}, page = {page}")
        logger.info("wait 60 seconds")
        return []

    max_page = resp["maxPage"]
    ls = resp["list"]
    if page < max_page:
        time.sleep(random.uniform(1, 5))
        return req_json(uid, page + 1) + ls

    return ls


def parse_json(ls: list):
    res = []
    for item in ls:
        res.append({
            "id": item["id"],
            "uid": item["user_id"],
            "title": item["title"],
            "content": item["description"].replace("<br/>", "\n"),
            "timestamp": datetime.fromtimestamp(item["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        })

    return res


def main():
    uid_stk = [9210717241]
    while len(uid_stk):
        uid = uid_stk.pop()
        ls = req_json(uid, 1)
        res = parse_json(ls)

        with open(f"timelines/{uid}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(res, ensure_ascii=False))

        logger.info(f"success => uid = {uid}, cnt = {len(res)}")
        time.sleep(random.uniform(5, 15))


if __name__ == '__main__':
    failed = []
    main()
    if len(failed):
        with open("failed.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(failed, ensure_ascii=False))