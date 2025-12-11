"""Holds shared singletons for cache and navigation context."""

from .cache import F1Cache
from .context import Context

ctx = Context()
f1_cache = F1Cache()


