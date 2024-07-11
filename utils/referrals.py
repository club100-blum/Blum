from asyncio import Semaphore
from typing import List
import secrets

import aiohttp
from aiohttp_proxy import ProxyConnector

from .agents import generate_random_user_agent
from utils.core import logger
from utils.telegram import AccountInterface
from utils.proxy import to_url
from utils.blum import BlumBot, RefCodeError, AccountUsedError
from utils import db
from data import config

try:
    from aiocfscrape import CloudflareScraper
    Session = CloudflareScraper
except:
    logger.info("Error when importing aiocfscrape.CloudflareScraper, using aiohttp.ClientSession instead")
    Session = aiohttp.ClientSession



sem = Semaphore(config.ACCOUNT_PER_ONCE)
async def make_referrals(accounts: List[AccountInterface], refcode: str):
    await db.init_db()
    used_accounts = await db.get_all_accounts()
    used_sessions = [account.id.removeprefix('sessions/') for account in used_accounts]
    logger.info(f"{len(used_accounts)} accounts are already registered")
    accounts_to_proccess = [account for account in accounts if account.name.removeprefix('sessions/').removesuffix('.session') not in used_sessions]
    for account in accounts_to_proccess:
        try:
            await account.get_tg_web_data(referral_code=refcode)
        except Exception as e:
            logger.error(f"{account} | {e}")
            continue
        logger.success(f"{account} | Got web data!")
        async with sem:
            proxy = account.get_proxy()
            if proxy is None:
                connector = None
            else:
                connector = ProxyConnector.from_url(to_url(proxy))
            async with Session(headers={'User-Agent': generate_random_user_agent(device_type='android',
                                                                                        browser_type='chrome')},
                                        timeout=aiohttp.ClientTimeout(total=60), connector=connector) as session:
                blum = BlumBot(account=account, session=session)
                try:
                    await blum.register(refcode, f'user{secrets.token_hex(3)}')
                except AccountUsedError:
                    logger.error(f"{account} | Account is already used")
                    continue
                except RefCodeError as e:
                    await db.referral_unavailable(refcode)
                    logger.error(f"{account} | {e}")
                    acc = await db.get_free_referrer(config.REFERRAL_COUNT)
                    if acc is None:
                        logger.error(f"{account} | No free referrer found!")
                        return
                    refcode = acc.referral_code
                    try:
                        await blum.register(refcode, f'user{secrets.token_hex(3)}')
                    except AccountUsedError:
                        logger.error(f"{account} | Account is already used")
                        continue
                    except Exception as e:
                        logger.error(f"{account} | {e}")
                        logger.error(f"{account} | No free referrer found!")
                        return
                    continue
                except Exception as e:
                    logger.error(f"{account} | {e}")
                    continue
                
                logger.success(f"{account} | Registered with refcode {refcode}")
                try:
                    await db.add_account(account.name, referral_code=await blum.get_referral_code(), referral_id=refcode)
                    await db.increment_referrals_count(refcode)
                except:
                    logger.error(f"{account} | Failed to add account to db")
