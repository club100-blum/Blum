from __future__ import annotations
from typing import Optional, List
import os
from os.path import join
from abc import ABC, abstractmethod
from itertools import cycle

from pyrogram import Client
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView

from data import config
from utils.core import logger
from utils.proxy import to_pyrogram
from urllib.parse import unquote
from .base import AccountInterface, AuthError



class PyrogramAccount(AccountInterface):
    def __init__(
            self, 
            name: str,
            proxy: Optional[str] = None
            ):
        self.name = name
        self.proxy = proxy
        self.telegram_name = None
        self.client = Client(
            name=name, 
            api_id=config.API_ID, 
            api_hash=config.API_HASH,
            proxy=to_pyrogram(proxy))
        
    def get_proxy(self) -> Optional[str]:
        return self.proxy
        
    async def get_tg_web_data(self, referral_code: Optional[str] = None):
        """
        Get the Telegram web data needed for login.
        """
        try:
            await self.client.connect()
            me = await self.client.get_me()
            if not me:
                raise AuthError("Failed to get Telegram details")
            if me.username:
                self.telegram_name = f'@{me.username}'
            else:
                self.telegram_name = me.first_name
        except Exception as e:
            raise AuthError(f"Failed to connect: {e}")
        
        web_view = await self.client.invoke(
            RequestAppWebView(
                peer = 'BlumCryptoBot',
                app = InputBotAppShortName(await self.client.resolve_peer('BlumCryptoBot'), 'app'),
                platform = 'android',
                start_param=f'ref_{referral_code}' if referral_code else None
            )
        )
        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

    @staticmethod
    def get_accounts(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[PyrogramAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".session"):
                session = file.replace(".session", "")
                accounts.append(
                    PyrogramAccount(name=join(folder_path, session), proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} pyrogram accounts")
        return accounts
    
    def __str__(self):
        return str(self.telegram_name or self.name)