import collections
import time
from typing import Any, Callable, Dict, Iterable, TypeVar, Tuple, List, Optional

from discord.ext import commands


# Like discord.py's SequenceProxy, but for key/value stores.
class MappingProxy(collections.abc.Mapping):
    def __init__(self, proxied):
        self.__proxied: Dict[Any, Any] = proxied

    def __getitem__(self, idx):
        return self.__proxied[idx]

    def __len__(self):
        return len(self.__proxied)

    def __contains__(self, item):
        return item in self.__proxied

    def __iter__(self):
        return iter(self.__proxied)

    def keys(self):
        return self.__proxied.keys()

    def items(self):
        return self.__proxied.items()

    def values(self):
        return self.__proxied.values()

    def get(self, *args, **kwargs):
        return self.__proxied.get(*args, **kwargs)


# Like discord.py's CooldownMapping, but simpler and usable outside of a command context
class SpamLimit:
    def __init__(self, original: commands.Cooldown):
        self._cache: Dict[int, commands.Cooldown] = {}
        self._cooldown = original

    def _verify_cache_integrity(self):
        current = time.time()
        dead_keys = [k for k, v in self._cache.items() if current > v._last + v.per]
        for k in dead_keys:
            del self._cache[k]

    def get_user(self, user_id: int):
        self._verify_cache_integrity()

        if user_id not in self._cache:
            bucket = self._cooldown.copy()
            self._cache[user_id] = bucket
        else:
            bucket = self._cache[user_id]

        return bucket


T = TypeVar('T')
def partition(iterable: Iterable[T], predicate: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
    ret = ([], [])
    for x in iterable:
        ret[predicate(x)].append(x)
    return ret


KEYPAD_UTF8 = b'\xef\xb8\x8f\xe2\x83\xa3'

def make_keypad(num: int) -> Optional[str]:
    if not (0 <= num <= 9):
        return None
    return (str(num).encode() + KEYPAD_UTF8).decode()

def parse_keypad(emoji: str) -> Optional[int]:
    b: bytes = emoji.encode()
    if len(b) < 2 or b[1:] != KEYPAD_UTF8:
        return None
    num = int(chr(b[0]))
    if not (0 <= num <= 9):
        return None
    return num
