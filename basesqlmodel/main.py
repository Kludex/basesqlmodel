from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, List, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

Self = TypeVar("Self", bound="Base")


class InvalidTable(RuntimeError):
    """Raised when calling a method coupled to SQLAlchemy operations.

    It should be called only by SQLModel objects that are tables.
    """


def is_table(cls: Type[Self]) -> bool:
    base_is_table = False
    for base in cls.__bases__:
        config = getattr(base, "__config__")
        if config and getattr(config, "table", False):
            base_is_table = True
            break
    return getattr(cls.__config__, "table", False) and not base_is_table


def validate_table(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        cls = self if inspect.isclass(self) else self.__class__
        if not is_table(cls):
            raise InvalidTable(
                f'"{cls.__name__}" is not a table. '
                "Add the class parameter `table=True` or don't use with this object."
            )
        return func(self, *args, **kwargs)

    return wrapper


class Base(SQLModel):
    @classmethod
    @validate_table
    async def get(
        cls: Type[Self], session: AsyncSession, *args: Any, **kwargs: Any
    ) -> Self:
        result = await session.execute(select(cls).filter(*args).filter_by(**kwargs))
        return result.scalars().first()

    @classmethod
    @validate_table
    async def get_multi(
        cls: Type[Self],
        session: AsyncSession,
        *args,
        offset: int = 0,
        limit: int = 100,
        **kwargs,
    ) -> List[Self]:
        result = await session.execute(
            select(cls).filter(*args).filter_by(**kwargs).offset(offset).limit(limit)
        )
        return result.scalars().all()

    @classmethod
    @validate_table
    async def create(cls: Type[Self], session: AsyncSession, **kwargs: Any) -> Self:
        db_obj = cls(**kwargs)
        session.add(db_obj)
        await session.commit()
        return db_obj

    @validate_table
    async def update(self: Self, session: AsyncSession, **kwargs: Any) -> Self:
        obj_data = jsonable_encoder(self)
        for field in obj_data:
            if field in kwargs:
                setattr(self, field, kwargs[field])
        session.add(self)
        await session.commit()
        await session.refresh(self)
        return self

    @classmethod
    @validate_table
    async def delete(
        cls: Type[Self], session: AsyncSession, *args: Any, **kwargs: Any
    ) -> Self:
        db_obj = await cls.get(session, *args, **kwargs)
        await session.delete(db_obj)
        await session.commit()
        return db_obj
