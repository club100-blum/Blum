from asyncio import sleep, Semaphore
from random import uniform
from typing import Union

import aiohttp
from aiohttp_proxy import ProxyConnector

from .agents import generate_random_user_agent
from data import config
from utils.blum import BlumBot
from utils.core import logger
from utils.helper import format_duration
from utils.telegram import AccountInterface
from utils.proxy import to_url

try:
    from aiocfscrape import CloudflareScraper
    Session = CloudflareScraper
except:
    logger.info("Error when importing aiocfscrape.CloudflareScraper, using aiohttp.ClientSession instead")
    Session = aiohttp.ClientSession


sem = Semaphore(config.ACCOUNT_PER_ONCE)
async def start(account: AccountInterface, tribe):
    sleep_dur = 0
    while True:
        await sleep(sleep_dur)
        async with sem:
            proxy = account.get_proxy()
            if proxy is None:
                connector = None
            else:
                connector = ProxyConnector.from_url(to_url(proxy))
            async with Session(headers={'User-Agent': generate_random_user_agent(device_type='android',
                                                                                        browser_type='chrome')},
                                        timeout=aiohttp.ClientTimeout(total=60), connector=connector) as session:
                try:
                    blum = BlumBot(account=account, session=session)
                    max_try = 2
                    await sleep(uniform(*config.DELAYS['ACCOUNT']))
                    a=await blum.login()
                   # logger.info(f"{account} | {a}")
                    a=await blum.tribe_login()


                    try:
                        msg = await blum.claim_daily_reward()
                        if isinstance(msg, bool) and msg:
                            logger.success(f"{account} | Claimed daily reward!")

                        timestamp, start_time, end_time, play_passes = await blum.balance()

                        claim_amount, is_available = await blum.friend_balance()
                        # logger.info(f"{account} | {claim_amount} | {is_available}")
                        if claim_amount != 0 and is_available:
                            amount = await blum.friend_claim()
                            logger.success(f"{account} | Claimed friend ref reward {amount}")

                        if config.PLAY_GAMES is False:
                            play_passes = 0
                        elif play_passes and play_passes > 0 and config.PLAY_GAMES is True:
                            await blum.play_game(play_passes)

                        await sleep(uniform(3, 10))

                        try:
                            timestamp, start_time, end_time, play_passes = await blum.balance()
                            if start_time is None and end_time is None and max_try > 0:
                                await blum.start()
                                logger.info(f"{account} | Start farming!")
                                max_try -= 1

                            elif (start_time is not None and end_time is not None and timestamp is not None and 
                                    timestamp >= end_time and max_try > 0):
                                await blum.refresh()
                                timestamp, balance = await blum.claim()
                                logger.success(f"{account} | Claimed reward! Balance: {balance}")
                                max_try -= 1

                            elif end_time is not None and timestamp is not None:
                                sleep_dur = end_time - timestamp
                                logger.info(f"{account} | Sleep {format_duration(sleep_dur)}")
                                max_try += 1
                                continue

                            elif max_try == 0:
                                break

                        except Exception as e:
                            if "NoneType" in str(e):
                                logger.info(f"{account} | Недостаточно билетов..")
                            else:
                                logger.error(f"{account} | Error: {e}")



                    except Exception as e:
                        logger.error(f"{account} | Error: {e}")
                except Exception as outer_e:
                    logger.error(f"{account} | Session error: {outer_e}")
        logger.info(f"{account} | Reconnecting in {format_duration(config.ITERATION_DURATION)}...")
        sleep_dur = config.ITERATION_DURATION


async def stats():
    logger.success("Analytics disabled")
