import importlib.metadata as importlib_metadata

from basesqlmodel.main import Base

__version__ = importlib_metadata.version(__name__)

__all__ = ["Base"]
