import sys
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("lcd1602")
except PackageNotFoundError:
    __version__ = "unknown"

from .lcd1602 import LCD1602, LCDAlignment
