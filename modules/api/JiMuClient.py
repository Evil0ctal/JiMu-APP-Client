#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author: https://github.com/Evil0ctal/
# @Time: 2023/04/30
# @Function:
# 对积目APP的API进行封装，方便使用。

import asyncio
import hashlib
import httpx
import json

from typing import Optional


class JiMuClient:

    def __init__(self):
        self.headers = {
            'User-Agent': 'okhttp/4.1.1',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json; charset=UTF-8',
        }
        self.timeout = 10
        self.sid = None
        self.uid = None
        self.service_host = 'https://service.hitup.cn'
        self.security_host = 'https://security.hitup.cn'

    @staticmethod
    def generate_md5(data: str):
        """
        :param data: 要哈希的数据（字符串类型）
        :return: MD5哈希值（16进制字符串类型）
        """
        md5 = hashlib.md5()
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()

    async def request(self, method, url, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, timeout=self.timeout, **kwargs)
        data = response.json()
        return data

    async def get(self, url: str, params=None):
        return await self.request(method="GET", url=url, params=params)

    async def post(self, url: str, data: dict):
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return await self.request(method="POST", url=url,
                                  content=json_str.encode("utf-8"))

    async def register(self, phone_country_code: int,
                       phone_number: int,
                       password: str,
                       password_md5: Optional[str] = None,
                       ) -> dict:
        pass

    async def login(self, phone_country_code: int,
                    phone_number: int,
                    password: str,
                    password_md5: Optional[str] = None,
                    ) -> dict:
        """
        :param phone_country_code: 手机号国家代码
        :param phone_number: 手机号
        :param password: 明文密码
        :param password_md5: 密码的MD5值
        :return: dict
        """
        url = f"{self.security_host}/api/v3/account/login?cv=GM5.5.90_Android"
        payload = {
            "account": f"{phone_country_code}{phone_number}",
            "nation_code": str(phone_country_code),
            "password": password_md5 or self.generate_md5(password)
        }
        response = await self.post(url, payload)
        if response["code"] != 0:
            raise ValueError(response['message'])
        # 更新sid和uid的类属性
        self.sid = response["data"]["token"]
        self.uid = response["data"]["uid"]
        return response

    async def get_self_info(self, sid: str = None, self_uid: int = None) -> dict:
        """
        :param sid: session id，运行login()后会自动更新。
        :param self_uid: 本人的uid，运行login()后会自动更新。
        :return: dict
        """
        sid = sid or self.sid
        self_uid = self_uid or self.uid
        if sid and self_uid:
            url = f"{self.service_host}/api/account/getMyself?cv=GM5.5.90_Android&statistics=&sid={sid}&uid={self_uid}"
            payload = {"id": self_uid}
            response = await self.post(url, payload)
            return response
        else:
            raise ValueError("请先登录！")

    async def get_user_info(self, target_uid: int, sid: str = None, self_uid: int = None) -> dict:
        """
        :param target_uid: 目标用户的uid
        :param sid: session id，运行login()后会自动更新。
        :param self_uid: 本人的uid，运行login()后会自动更新。
        :return: dict
        """
        sid = sid or self.sid
        self_uid = self_uid or self.uid
        if sid and self_uid:
            url = f"{self.service_host}/api/account/getUser?cv=GM5.5.90_Android&sid={sid}&uid={self_uid}"
            payload = {
                "from": 0,
                "id": target_uid
            }
            response = await self.post(url, payload)
            return response
        else:
            raise ValueError("sid or uid is None, please run self.login() first!")


if __name__ == '__main__':
    client = JiMuClient()
    asyncio.run(client.login(1, 4080000000, "Admin123456"))
    print(client.sid)
    print(client.uid)
    print(asyncio.run(client.get_user_info(2889383)))
