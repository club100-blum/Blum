from os.path import split, join, isfile
from typing import List

import psutil
from telethon.sessions import StringSession

from utils.core.tdata import DecryptError, convert_tdata
from utils.core.logger import logger
from .telethon import TelethonAccount, TelethonParams



def get_telegrams() -> List[TelethonAccount]:
    accounts = []
    for proc in psutil.process_iter():
        if 'telegram' in proc.name().lower():
            try:
                path =  join(split(proc.exe())[0], 'tdata')
            except:
                continue
            
            if isfile(join(path, 'passcode')):
                with open(join(path, 'passcode'), 'r', encoding='utf8') as f:
                    passcode = f.read()
            else:
                passcode = ''
            
            sessions = []
            while True:
                try:
                    sessions = convert_tdata(path, passcode.strip())
                    with open(join(path, 'passcode'), 'w', encoding='utf8') as f:
                        f.write(passcode)
                except DecryptError:
                    passcode = input(f'Enter passcode for "{proc.name()}" (or SKIP to skip): ')
                    if passcode.strip() == 'SKIP':
                        break
                else:
                    break
            logger.info(f'Found {len(sessions)} sessions in proccess "{proc.name()}"')
            
            for session in sessions:
                accounts.append(
                    TelethonAccount(session_params=TelethonParams(
                        session=StringSession(session),
                        api_id=2040,
                        api_hash='b18441a1ff607e10a989891a5462e627',
                        device_model='Desktop',
                        system_version='Windows 10',
                        app_version='4.15.1 x64',
                        lang_code='en',
                        system_lang_code='en-us'
                    ))
                )
    return accounts