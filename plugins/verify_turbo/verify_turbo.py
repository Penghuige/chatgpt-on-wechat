# encoding:utf-8

import json
import os
import random
import re
import time

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

# 这个文件用来实现功能：添加好友后进行判断，若发送邀请码且邀请码
# 正确，则能使用机器人的功能，若不正确则不行
# 刚加好友的时候能够获得一天试用，通过自身发送激活码来激活

@plugins.register(
    name="VerifyTurbo",
    desire_priority=100,
    hidden=True,
    desc="通过激活码与邀请码来获得机器人的使用权限。",
    version="1.0",
    author="lanvent",
)
class VerifyTurbo(Plugin):
    def __init__(self):
        super().__init__()
        try:
            # load config
            conf = super().load_config()
            curdir = os.path.dirname(__file__)
            if not conf:
                # 配置不存在则报错
                raise Exception("config.json not found")            # 创建一个空数组来存储邀请码
            self.invitation_code = {}
        except Exception as e:
            logger.warn("[VerifyTurbo] init failed, ignore or see")
            raise e
    
    def generate_invitation_code(self):
        """生成随机的邀请码"""
        # 这里使用简单的随机生成方式，你可以根据需要改进
        return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(6, 10)))
    
    def send_invitation(self, friend_id):
        """发送邀请码给好友"""
        invitation_code = self.generate_invitation_code()
        self.invitation_codes[invitation_code] = friend_id  # 存储邀请码和好友ID
        invitation_message = f"欢迎加入我们！请使用以下邀请码进行验证：{invitation_code}"
    
    def verify_invitation(self, received_code):
        """验证邀请码是否正确"""
        # 使用正则表达式匹配“激活码: 邀请码”格式
        pattern = re.compile(r'^(激活码|激活碼)[:：]\s*([A-Za-z0-9]+[A-Za-z0-9]$)')
        match = pattern.match(received_code)
        if match:
            activation_code = match.group(1)
            # 兑换后删除邀请码
            self.invitation_code.pop(activation_code, None)
            if activation_code in self.invitation_codes:
                invitation_data = self.invitation_codes[activation_code]
                current_time = time.time()
                # 计算剩余时限（假设时限为1小时）
                remaining_time = 3600 - (current_time - invitation_data['timestamp'])
                return f"激活码 {activation_code} 剩余有效时间：{int(remaining_time // 60)} 分钟 {int(remaining_time % 60)} 秒"
            else:
                return "无效的激活码"
        else:
            return "格式错误"
        
    def get_help_text(self, **kwargs):
        help_text = (
            "通过激活码与邀请码来获得机器人的使用权限。"
        )
        return help_text
        
