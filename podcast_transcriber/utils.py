import re
from datetime import timedelta as TimeDelta
from pathlib import Path
from random import shuffle
from typing import Dict, Generator, List, Tuple, TypeVar

SLUGIFY_PATTERN = re.compile(r"\W+")

A = TypeVar("A")
B = TypeVar("B")
K = TypeVar("K")
T = TypeVar("T")


def slugify(s: str) -> str:
    return re.sub(SLUGIFY_PATTERN, "-", s).lower()


def zip_join(
    a: Dict[K, A],
    b: Dict[K, B],
) -> Generator[Tuple[K, A, B], None, None]:
    keys = a.keys() | b.keys()
    for key in keys:
        yield (key, a[key], b[key])


def create_parent_folder(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def shuffled_list(x: List[T]) -> List[T]:
    shuffle(x)
    return x


def shuffled_dict(d: Dict[K, T]) -> Dict[K, T]:
    return {k: d[k] for k in shuffled_list(list(d.keys()))}


def seconds_to_timestamp(n_seconds: float) -> str:
    return str(TimeDelta(seconds=round(n_seconds)))
