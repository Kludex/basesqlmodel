<h1 align="center">
    <strong>Base SQLModel</strong>
</h1>
<p align="center">
    <a href="https://github.com/Kludex/basesqlmodel" target="_blank">
        <img src="https://img.shields.io/github/last-commit/Kludex/basesqlmodel" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/Kludex/basesqlmodel/Test">
        <img src="https://img.shields.io/codecov/c/github/Kludex/basesqlmodel">
    <br />
    <a href="https://pypi.org/project/basesqlmodel" target="_blank">
        <img src="https://img.shields.io/pypi/v/basesqlmodel" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/basesqlmodel">
    <img src="https://img.shields.io/github/license/Kludex/basesqlmodel">
    <p align="center"><i> A very simple CRUD class for SQLModel! ✨ </i></p>
</p>



Inspired by:
- [Full Stack FastAPI and PostgreSQL - Base Project Generator](https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/crud/base.py)
- [FastAPI Microservices](https://github.com/Kludex/fastapi-microservices/blob/main/users/app/crud/base.py)


## Installation

``` bash
pip install basesqlmodel
```

## Usage

```python
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field

from basesqlmodel import Base

engine = create_async_engine("sqlite+aiosqlite:///:memory:")
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Potato(Base, table=True):
    id: int = Field(primary_key=True)
    name: str


async def main():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Interact with the Potato table
    async with SessionLocal() as session:
        obj = await Potato.create(session, name="Potato")
        print(f"Potato created: {repr(obj)}")

        obj = await Potato.get(session, name="Potato")
        print(f"Potato retrieved: {repr(obj)}")

        await obj.update(session, name="Fake Potato")
        print(f"Potato updated: {repr(obj)}")

        await Potato.delete(session, name="Fake Potato")
        print(f"Potato deleted: {repr(obj)}")

        objs = await Potato.get_multi(session)
        print(f"Confirm that the database is empty: {objs}")


asyncio.run(main())
```

## License

This project is licensed under the terms of the MIT license.
