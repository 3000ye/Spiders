import time
import random
import requests
import re
import os
import json

from utils.logger import Logger
logger = Logger(name="XueQiu members")


headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "referer": "https://xueqiu.com/"
}

cookie = "cookiesu=771740236235970; Hm_lvt_1db88642e346389874251b5a1eded6e3=1740236236; HMACCOUNT=FA22D531B8DD38C5; device_id=98e60459e4744dc65d7e96f3806fbf04; s=bv11co2fy0; bid=2cf207f1534b00bf635945ffaac73030_m7gbvfmj; snbim_minify=true; remember=1; xq_a_token=345d667ef7e914cfb820b0dd92324df2dfdc3789; xqat=345d667ef7e914cfb820b0dd92324df2dfdc3789; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjUwNTk1NDU3OTEsImlzcyI6InVjIiwiZXhwIjoxNzQyOTU4Njc0LCJjdG0iOjE3NDAzODIwNjE1MzAsImNpZCI6ImQ5ZDBuNEFadXAifQ.hXJrtwC2Q6veA3thWWERQXJH7VqKSH6uoRpWhbUlK1VfPZtb8EdUqU7pwJXiWNT0fSamdnLcJxoMbUNdX7dpmzVZoGQmTdWKVeNhWnvtsN-QiAZZHF9VioZ6GUpKjaBNa2T5DRQ7V1rlraOGz2dX5oGKhh6OegV9y3NaPyyMbkgXGogRADjFRq8wiZb_HChUGFDLDzqrLApssfTzKgvsNAcFYsx_5COOT3JQyovfUirHRFoMWwlNDoR1EeZNfUR7Z_BKE2DhGjxmVye7EsVr4W-QcmXes-dr0oDUR_gXVPkUD7528zSM5kso5686X2nxmouMQoa956e3Creiv6YAUQ; xq_r_token=9c0cb4a4e479edbf86f365e29b60668aa4a884c6; xq_is_login=1; u=5059545791; acw_tc=0b32973a17404023884542723ebd51652a12ad5268aa1a0d58cd3d7f9a1412; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1740402583; ssxmod_itna=YqUhD5AK7IMDkFDXKDHD0W5biQeD=Hhqo5q5Cobs1Dlp3xA5D8D6DQeGTbcs5HWUiSb+e6bCO45DgQBRdvNZ0guLWKL22qF4CSYxiTD4q07Db4GkDAqiOD7LuKDxpq0rD74irDDxD3RxDtD1w=D7ONS0wN07T=2CkNDm+=nDGQ9DiUQxi5ePm0ZDMwZDD3QxB6qxA3nD7tDOwQDbqDump63yqDLRjaONP=DbEpStZWDtqnnYL4V4Ci94I+fKGPGtr4wB7xtt7EiFBxFY7hdBBx5ti+P/7hPbGGp/KYXfH+dYcdGFiD==; ssxmod_itna2=YqUhD5AK7IMDkFDXKDHD0W5biQeD=Hhqo5q5CobsD62tlrmlx055y4itDLCl6qTFdDw1hKGcDYI24qBiw0DxD==="
cookies = dict(re.findall(r'([^=;]+)=([^=;]+)', cookie))


def parse_user(uid: int, page: int):
    """
    爬取单个用户的关注列表，筛出粉丝数大于5万的用户
    """

    logger.info(f"uid = {uid}, page = {page}")

    url = f"https://xueqiu.com/friendships/groups/members.json?uid={uid}&page={page}&gid=0&md5__1038=n4Ix07G%3Diti%3DD%3DdiQD%2FQWoBIvhmbOdDBGlGoD"
    resp = requests.get(url, cookies=cookies, headers=headers)
    resp.encoding = "utf-8"
    resp = resp.json()

    if "users" not in resp.keys():
        return []

    max_page = resp["maxPage"]
    users: list = resp["users"]
    users = list(filter(lambda u: u["followers_count"] >= 50000, users))

    if page < max_page:
        time.sleep(random.uniform(0, 1))
        return parse_user(uid, page + 1) + users

    return users


def count_user():
    """
    合并 json
    """

    files = os.listdir("uid")

    us = []
    is_cnt = []
    for file in files:
        file_path = os.path.join("uid", file)
        logger.info(f"read {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            ls = json.loads(f.read())

        for u in ls:
            if u["id"] in is_cnt:
                continue
            us.append({
                "uid": u["id"],
                "name": u["screen_name"],
                "fans_cnt": u["followers_count"],
                "description": u["description"],
                "verified_infos": u["verified_infos"]
            })
            is_cnt.append(u["id"])

    us.sort(key=lambda u: u["fans_cnt"], reverse=True)

    with open("V.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(us, ensure_ascii=False))


def gen_stack():
    with open("V.json", "r", encoding="utf-8") as f:
        ls = json.loads(f.read())

    stk = [i["uid"] for i in ls]
    return stk


def main():
    stk = gen_stack()
    is_parsed = []

    while len(stk) > 0:
        uid = stk.pop()

        if uid in is_parsed:
            continue

        logger.info(f"uid = {uid}, parsing")

        temp = parse_user(uid, 1)
        is_parsed.append(uid)

        logger.info(f"uid = {uid}, found {len(temp)} users")
        time.sleep(random.uniform(1, 5))

        for u in temp:
            stk.append(u["id"])
        with open(f"uid/{uid}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(temp, ensure_ascii=False))


if __name__ == '__main__':
    # main()
    # count_user()

    with open("V.json", "r", encoding="utf-8") as f:
        ls = json.loads(f.read())

    res = []
    for u in ls:
        if u["verified_infos"] and "雪" not in u["verified_infos"][0]["verified_desc"]:
            res.append(u)

    with open("V.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(res, ensure_ascii=False))