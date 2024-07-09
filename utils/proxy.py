from typing import Optional

from .phone import parse_country_code
from data import config


def to_telethon(proxy: Optional[str]):
    if proxy is None:
        return None
    
    creds, address = proxy.split('@')
    if creds:
        user, pswd = creds.split(':')
    else:
        user, pswd = None, None
    host, port = address.split(':')
    return ('http', host, int(port), True, user, pswd)

def to_pyrogram(proxy: Optional[str]):
    if proxy is None:
        return None
    
    creds, address = proxy.split('@')
    if creds:
        user, pswd = creds.split(':')
    else:
        user, pswd = '', ''
    host, port = address.split(':')
    return {
        "hostname": host,
        "port": int(port),
        "username": user,
        "password": pswd
    }

def to_url(proxy: Optional[str]):
    if proxy is None:
        return None
    
    return f"http://{proxy}"

def get_dataimpulse_proxy_by_country(country: str, proxy_id: int = 0) -> str:
    '''
    country: str - country code "us", "kz", "ru", etc.
    '''
    return f'{config.DI_LOGIN}__cr.{country.lower()}:{config.DI_PASSWORD}@gw.dataimpulse.com:{10000 + proxy_id}'

def get_dataimpulse_proxy_by_phone(phone_number: str, proxy_id: int = 0) -> str:
    country, code = parse_country_code(phone_number)
    return get_dataimpulse_proxy_by_country(country, proxy_id=proxy_id)