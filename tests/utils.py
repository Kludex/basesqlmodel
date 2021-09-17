from sqlmodel import Field

from basesqlmodel import Base


class Potato(Base, table=True):
    id: int = Field(primary_key=True)
    name: str
