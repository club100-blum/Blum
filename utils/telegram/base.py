from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional


class AuthError(Exception):
    ...
    
class AccountInterface(ABC):
    @abstractmethod
    def get_proxy(self) -> Optional[str]:
        pass
    
    @abstractmethod
    async def get_tg_web_data(self, referral_code: Optional[str] = None) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    async def get_accounts(
            folder_path: str, 
            proxies: Optional[List[str]] = None
            ) -> List[AccountInterface]:
        pass
    
    @abstractmethod
    async def __str__(self) -> str:
        pass