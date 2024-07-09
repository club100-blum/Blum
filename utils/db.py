from typing import Optional, List

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, Integer, select, Boolean, and_
from sqlalchemy.orm import relationship, sessionmaker

from data import config



Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(String, primary_key=True, index=True)
    referral_avaialble = Column(Boolean, default=True)
    referral_code = Column(String, nullable=True)
    referral_id = Column(String, ForeignKey('accounts.id'), nullable=True)
    referrals_count = Column(Integer, default=0)
    referrals = relationship('Account', backref='referrer', remote_side=[id])
    joined_channels = relationship('JoinedChannel', back_populates='account')
    
    def __repr__(self):
        return f'<Account id={self.id} referrals_count={self.referrals_count}>'

class JoinedChannel(Base):
    __tablename__ = 'joined_channels'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(String, ForeignKey('accounts.id'), nullable=False)
    channel_link = Column(String, nullable=False)
    account = relationship('Account', back_populates='joined_channels')

    def __repr__(self):
        return f'<JoinedChannel id={self.id} account_id={self.account_id} channel_link={self.channel_link}>'

engine = create_async_engine(config.DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

class DbSession:
    '''
    Class wrapper for adding type hints to the AsyncSessionLocal
    '''
    def __init__(self):
        self.session = AsyncSessionLocal()

    async def __aenter__(self) -> AsyncSession:
        await self.session.__aenter__()
        return self.session

    async def __aexit__(self, *args):
        await self.session.__aexit__(*args)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_account(id: str) -> Optional[Account]:
    async with DbSession() as session:
        return await session.get(Account, id)

async def add_account(id: str, referral_code: Optional[str] = None, referral_id: Optional[str] = None):
    async with DbSession() as session:
        new_account = Account(id=id, referral_code=referral_code, referral_id=referral_id)
        session.add(new_account)
        await session.commit()
            
async def increment_referrals_count(referral_code: str):
    async with DbSession() as session:
        result = await session.execute(select(Account).where(Account.referral_code == referral_code))
        account = result.scalars().first()
        if account:
            account.referrals_count += 1
            await session.commit()
            
async def referral_unavailable(referral_code: str):
    async with DbSession() as session:
        result = await session.execute(select(Account).where(Account.referral_code == referral_code))
        account = result.scalars().first()
        if account:
            account.referral_avaialble = False
            await session.commit()

async def get_free_referrer(count: int = 2) -> Optional[Account]:
    '''
    Returns account with the referral_count less than "count" param (desc), or None if there is no such account
    '''
    async with DbSession() as session:
        result = await session.execute(
            select(Account).where(
                and_(
                    Account.referrals_count < count,
                    Account.referral_code != None,
                    Account.referral_avaialble == True
                )
            ).order_by(Account.referrals_count.desc()).limit(1)
        )
        return result.scalars().first()
    
async def add_joined_channel(account_id: str, channel_link: str):
    async with DbSession() as session:
        new_channel = JoinedChannel(account_id=account_id, channel_link=channel_link)
        session.add(new_channel)
        await session.commit()

async def get_joined_channels(account_id: str) -> List[JoinedChannel]:
    async with DbSession() as session:
        result = await session.execute(select(JoinedChannel).where(JoinedChannel.account_id == account_id))
        return result.scalars().all()
    
async def get_all_accounts() -> List[Account]:
    async with DbSession() as session:
        result = await session.execute(select(Account))
        return result.scalars().all()