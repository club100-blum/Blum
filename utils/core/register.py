import os
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from utils.core import logger
from data import config


async def create_sessions():
    sessions_dir = "sessions"
    os.makedirs(sessions_dir, exist_ok=True)

    while True:
        session_name = input('\nВведите название сессии (для выхода нажмите Enter):\nWrite a session name and '
                             'press enter: ')
        if not session_name:
            return

        session_path = os.path.join(sessions_dir, session_name)

        client = TelegramClient(
            session=session_path,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
        )

        try:
            async with client:
                user_data = await client.get_me()

                logger.success(
                    f'Успешно добавлена сессия {user_data.username or "No username"} | {user_data.phone or "No phone"}\n'
                    f'Session saved in {session_path}')
        except PhoneNumberInvalidError:
            logger.error("Некорректный номер телефона. Проверьте и попробуйте снова.")
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
