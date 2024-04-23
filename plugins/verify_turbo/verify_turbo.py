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
    hidden=False,
    desc="通过激活码与邀请码来获得机器人的使用权限。",
    version="1.0",
    author="Penghuige",
)
class VerifyTurbo(Plugin):
    def __init__(self):
        super().__init__()
        try:
            # load config
            conf = super().load_config()
            if not conf:
                # 配置不存在则报错
                raise Exception("config.json not found")            # 创建一个空数组来存储邀请码
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            # 这个字典要存储邀请码和好友ID还有邀请码的时间
            self.invitation_codes = {}
        except Exception as e:
            logger.warn("[VerifyTurbo] init failed, ignore or see")
            raise e
    
    def on_handle_context(self, e_context: EventContext):
        # 根据输入判断使用功能
        if e_context["context"].type != ContextType.TEXT:
            return
        content = e_context["context"].content
        if content.startswith("激活码"):
            # 发送激活码 这里要辨别是不是正确的，不是就返回错误
            # verify_invitation
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = self.verify_invitation(content)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        elif content.startswith("邀请码"):
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = self.verify_invitation(content)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        elif content == "申请邀请码":
            self.send_invitation(e_context["context"].sender_id)
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = "邀请码已发送，请查收。"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
        else:
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = "请发送“激活码”或“邀请码”来获取机器人的使用权限。"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS


    def generate_invitation_code(self):
        """生成随机的邀请码"""
        # 这里使用简单的随机生成方式，你可以根据需要改进
        return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(6, 10)))
    
    def send_invitation(self, friend_id):
        """发送邀请码给好友"""
        invitation_code = self.generate_invitation_code()
        # 存储邀请码和好友ID还有时间,但一时间可能有多个,这个数组要存很多个邀请码
        invitation_data = {"friend_id": friend_id, "time": time.time()}
        self.invitation_codes[invitation_code] = invitation_data
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
            # 判断是否过期 这里用到的invitation_data是一个字典，存储了邀请码和时间
            if time.time() - self.invitation_codes[received_code] > 86400:
                return False
            return True
        else:
            return False
        
    def display_all_invitation_codes(self):
        """展示所有邀请码及其所有信息"""
        return json.dumps(self.invitation_codes, indent=4, ensure_ascii=False)
        
    def get_help_text(self, **kwargs):
        help_text = (
            "通过激活码与邀请码来获得机器人的使用权限。"
        )
        return help_text