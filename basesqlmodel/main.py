from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Query, noload, raiseload, selectinload, subqueryload
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

Self = TypeVar("Self", bound="Base")
LoadStrategy = Literal["subquery", "selectin", "raise", "raise_on_sql", "noload"]
load_strategy_map: Dict[LoadStrategy, Callable[..., Any]] = {
    "subquery": subqueryload,
    "selectin": selectinload,
    "raise": raiseload,
    "raise_on_sql": raiseload,
    "noload": noload,
}


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


def _prepare_query(
    cls: Type[Self], load_strategy: Dict[str, LoadStrategy] | None
) -> Query:
    load_strategy = load_strategy or {}
    query = select(cls)
    for key, strategy in load_strategy.items():
        query = query.options(load_strategy_map[strategy](key))
    return query


class Base(SQLModel):
    @classmethod
    @validate_table
    async def get(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        load_strategy: Dict[str, LoadStrategy] = None,
        **kwargs: Any,
    ) -> Self:
        query = _prepare_query(cls, load_strategy)
        result = await session.execute(query.filter(*args).filter_by(**kwargs))
        return result.scalars().first()

    @classmethod
    @validate_table
    async def get_multi(
        cls: Type[Self],
        session: AsyncSession,
        *args: BinaryExpression,
        load_strategy: Dict[str, LoadStrategy] = None,
        offset: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> List[Self]:
        query = _prepare_query(cls, load_strategy)
        result = await session.execute(
            query.filter(*args).filter_by(**kwargs).offset(offset).limit(limit)
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
        cls: Type[Self], session: AsyncSession, *args: BinaryExpression, **kwargs: Any
    ) -> Self:
        db_obj = await cls.get(session, *args, **kwargs)
        await session.delete(db_obj)
        await session.commit()
        return db_obj
