import asyncio
from itertools import cycle
import os
from sys import platform
from typing import Iterable

from aiohttp import ClientSession

from utils.core import create_sessions, logger
from utils.telegram import PyrogramAccount, TelethonAccount, get_telegrams, AccountInterface
from utils.starter import start
from utils.core import get_all_lines
import argparse
from data import config
from utils.referrals import make_referrals



async def get_accounts():
    if config.PROXY is True:
        proxies = get_all_lines("data/proxy.txt")
    else:
        proxies = None
        
    if config.MODE == 'pyrogram':
        accounts = PyrogramAccount.get_accounts(folder_path=config.WORKDIR, proxies=proxies)
    elif config.MODE == 'telethon':
        accounts = TelethonAccount.get_accounts(folder_path=config.WORKDIR, proxies=proxies)
    elif config.MODE == 'telethon+json':
        if config.DATAIMPULSE:
            logger.info("Using dataimpulse.com proxies...")
            accounts = TelethonAccount.get_accounts_from_json_files_dataimpulse(folder_path=config.WORKDIR)
        else:
            accounts = TelethonAccount.get_accounts_from_json_files(folder_path=config.WORKDIR, 
                                                                    proxies=proxies)
    elif config.MODE == 'lazy':
        accounts = get_telegrams()
    return accounts
        

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')
    action = parser.parse_args().action

    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    if not os.path.exists('statistics'):
        os.mkdir('statistics')
    if not os.path.exists('statistics/opened_telegram_channels'):
        os.mkdir('statistics/opened_telegram_channels')

    await banner()

    if not action:
        action = int(input("Select action:\n1. Start soft\n2. Start blum with ref code from telegrams\n3. Create pyrogram sessions\n\n> "))

    if action == 3:
        await create_sessions()
        
    if action == 2:
        refcode = input("Enter initial referral code or link: ")
        refcode = refcode.removeprefix('https://')
        refcode = refcode.removeprefix('t.me/BlumCryptoBot/app?startapp=')
        refcode = refcode.removeprefix('ref_')
        logger.info(f'Referral code: {refcode}')
        accounts = await get_accounts()
        await make_referrals(accounts, refcode)

    if action == 1:
        accounts = await get_accounts()
        if not accounts:
            logger.error("No accounts found!")
            return
            
        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(start(account=account)))

        await asyncio.gather(*tasks)
        

async def banner():
    print(r"""

  ___   __  ____  __   ____  __   __     __   _  _  ____ 
 / __) / _\(_  _)/ _\ (  __)/ _\ (  )   /  \ / )( \(  __)
( (__ /    \ )( /    \ ) _)/    \/ (_/\(  O )) \/ ( ) _) 
 \___)\_/\_/(__)\_/\_/(__) \_/\_/\____/ \__\)\____/(____)
                                                         
            Catafalque Depo Scripts for The Club 100                                   
TON address for coffee: UQBhsu6Lsxu21AQdj6YMNdjCvCXuTxG-xdnWF4tOtQpICeiU
          """)
    
    async with ClientSession() as session:
        channel_link = await (await session.get('https://files.catafalque.su/blum/channel_link.txt')).text()
        app_version = await (await session.get('https://files.catafalque.su/blum/app_version.txt')).text()
        app_version = app_version.strip()
        channel_link = channel_link.strip()
    
    if config.APP_VERSION != app_version:
        logger.warning(f"Вышла новая версия: {app_version}. Скачайте на https://github.com/folqc-dev/Blum")
    
    channel_username = channel_link.split('/')[3] 
    if channel_username in os.listdir('statistics/opened_telegram_channels'):
        return
    else:
        with open(f'statistics/opened_telegram_channels/{channel_username}', 'w') as f:
            pass
        
        if platform == 'win32':
            os.system(f'start https://t.me/{channel_link.split("/",3)[3]}')
            logger.warning(f"Подпишитесь на канал автора https://t.me/{channel_username} в браузере. На следующем запуске ссылка открываться не будет.")
        elif platform == 'linux':
            logger.warning(f"Подпишитесь на канал автора https://t.me/{channel_username}")

if __name__ == '__main__':
    asyncio.run(main())

