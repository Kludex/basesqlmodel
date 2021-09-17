import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from basesqlmodel.main import Base, InvalidTable, is_table
from tests.utils import Potato


def test_is_table() -> None:
    assert is_table(Potato)

    class PotatoJunior(Potato):
        ...

    assert not is_table(PotatoJunior)


@pytest.mark.asyncio
async def test_invalid_table(session: AsyncSession) -> None:
    class Banana(Base):
        ...

    with pytest.raises(InvalidTable):
        await Base.get_multi(session)


@pytest.mark.asyncio
async def test_get(session: AsyncSession) -> None:
    obj = await Potato.create(session, name="Blue")
    assert await Potato.get(session, name="Blue") == obj


@pytest.mark.asyncio
async def test_get_multi(session: AsyncSession) -> None:
    for name in ("Red", "Green", "Blue"):
        await Potato.create(session, name=name)
    assert await Potato.get_multi(session, name="Red") == [Potato(id=1, name="Red")]
    assert len(await Potato.get_multi(session)) == 3


@pytest.mark.asyncio
async def test_update(session: AsyncSession) -> None:
    obj = await Potato.create(session, name="Blue")
    await obj.update(session, name="Green")


@pytest.mark.asyncio
async def test_delete(session: AsyncSession) -> None:
    obj = await Potato.create(session, name="Blue")
    assert await Potato.delete(session, name="Blue") == obj
