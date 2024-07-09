from __future__ import annotations
from typing import Optional, List
import os
from os.path import join
from dataclasses import dataclass, asdict
from itertools import cycle
import json

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputBotAppShortName, AppWebViewResultUrl
from telethon.tl.functions.messages import RequestAppWebViewRequest

from data import config
from utils.core import logger
from utils.proxy import to_telethon, get_dataimpulse_proxy_by_phone
from urllib.parse import unquote
from .base import AccountInterface, AuthError



@dataclass
class TelethonParams:
    session: str
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str
    
class TelethonAccount(AccountInterface):
    def __init__(
            self, 
            session_file: Optional[str] = None,
            session_params: Optional[TelethonParams] = None,
            proxy: Optional[str] = None
            ):
        self.telegram_name = None
        self.proxy = proxy
        if session_file is not None:
            self.client = TelegramClient(
                session=session_file, 
                api_id=config.API_ID, 
                api_hash=config.API_HASH, 
                proxy=to_telethon(proxy))
            self.name = session_file
        elif session_params is not None:
            self.client = TelegramClient(
                **asdict(session_params),
                proxy=to_telethon(proxy))
            self.name = session_params.session
        else:
            raise ValueError("Either session_file or session_params must be provided")
        if isinstance(self.name, StringSession):
            self.name = self.name.save()
        
    def get_proxy(self) -> Optional[str]:
        return self.proxy
        
    async def get_tg_web_data(self, referral_code: Optional[str] = None):
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
        
        try:
            webapp_response: AppWebViewResultUrl = await self.client(
                RequestAppWebViewRequest(
                    peer = 'BlumCryptoBot',
                    app = InputBotAppShortName(await self.client.get_input_entity('BlumCryptoBot'), 'app'),
                    platform = 'android',
                    start_param=f'ref_{referral_code}' if referral_code else None
                )
            )
        except Exception as e:
            raise AuthError(f"Failed to get web data: {e} | start_param={f'ref_{referral_code}' if referral_code else None}")
        await self.client.disconnect()
        return unquote(string=unquote(string=webapp_response.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
    
    @staticmethod
    def get_accounts(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".session"):
                session = file.replace(".session", "")
                accounts.append(
                    TelethonAccount(session_file=join(folder_path, session), proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts
    
    @staticmethod
    def json_to_params(
            json_data: dict, 
            path_prefix: Optional[str] = None
            ) -> TelethonParams:
        if path_prefix:
            session = join(path_prefix, json_data['session_file'])
        else:
            session = json_data['session_file']
        return TelethonParams(
            session=session, 
            api_id=json_data['app_id'], 
            api_hash=json_data['app_hash'],
            device_model=json_data['device'],
            system_version=json_data['sdk'],
            app_version=json_data['app_version'],
            lang_code=json_data.get('lang_pack') or json_data.get('lang_code'),
            system_lang_code=json_data.get('system_lang_pack') or json_data.get('system_lang_code'),
        )
    
    @staticmethod
    def get_accounts_from_json_files(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)
                
                accounts.append(
                    TelethonAccount(session_params=session_params, proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts
    
    @staticmethod
    def get_accounts_from_json_files(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[TelethonAccount]:
        accounts = []
        proxies_ = cycle(proxies) if proxies else cycle([None])
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)
                
                accounts.append(
                    TelethonAccount(session_params=session_params, proxy=next(proxies_))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts
    
    @staticmethod
    def get_accounts_from_json_files_dataimpulse(
            folder_path: str
            ) -> List[TelethonAccount]:
        accounts = []
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                with open(join(folder_path, file), 'r') as f:
                    session_params = TelethonAccount.json_to_params(json.load(f), path_prefix=folder_path)
                
                accounts.append(
                    TelethonAccount(session_params=session_params, 
                                    proxy=get_dataimpulse_proxy_by_phone(session_params.session.removesuffix('.session').removeprefix('sessions/')))
                )
        logger.info(f"Loaded {len(accounts)} telethon accounts")
        return accounts
    
    def __str__(self):
        return str(self.telegram_name or self.name)
    