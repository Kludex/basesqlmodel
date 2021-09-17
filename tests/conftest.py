import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlmodel.ext.asyncio.session import AsyncSession

from basesqlmodel import Base

engine = create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest.fixture()
async def connection() -> AsyncConnection:
    async with engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture()
async def session(connection: AsyncConnection):
    async with AsyncSession(connection, expire_on_commit=False) as _session:
        yield _session


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Reference: https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def init_database():
    import tests.utils  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
