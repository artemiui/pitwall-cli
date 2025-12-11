"""Simple caching layer for OpenF1 API responses."""

from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

from .colors import Color


class F1Cache:
    """Intelligent caching system for OpenF1 API data."""

    def __init__(self, cache_dir: str = "~/.f1cli_cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache expiration policies (in hours)
        self.expiration_policies = {
            "sessions": 24,  # Session lists change rarely
            "meetings": 24,  # Meeting info is stable
            "drivers": 12,  # Driver info per session
            "laps": 1,  # Lap data could be updated
            "stints": 1,  # Stint data
            "position": 0.5,  # Position data (30 min)
            "pit": 1,  # Pit stop data
            "results": 2,  # Session results
            "default": 6,  # Default for other endpoints
        }

    def _get_cache_key(self, url: str) -> str:
        """Generate a unique cache key from URL."""
        clean_url = url.replace("https://", "").replace("http://", "")
        return hashlib.md5(clean_url.encode()).hexdigest()

    def _get_endpoint_type(self, url: str) -> str:
        """Extract endpoint type from URL for expiration policy."""
        parts = url.split("/")
        if len(parts) >= 5:
            endpoint = parts[4].split("?")[0]
            return endpoint
        return "default"

    def get(self, url: str):
        """Retrieve data from cache if fresh."""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            endpoint_type = self._get_endpoint_type(url)
            expiration_hours = self.expiration_policies.get(
                endpoint_type, self.expiration_policies["default"]
            )

            cached_time = datetime.fromisoformat(cache_data["cached_at"])
            expiry_time = cached_time + timedelta(hours=expiration_hours)

            if datetime.now() < expiry_time:
                print(f"{Color.DIM}✓ Using cached {endpoint_type} data{Color.RESET}")
                return cache_data["data"]

            print(f"{Color.DIM}ℹ Cached {endpoint_type} data expired{Color.RESET}")
            return None

        except (json.JSONDecodeError, KeyError):
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, url: str, data: dict) -> None:
        """Store data in cache."""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            "url": url,
            "endpoint": self._get_endpoint_type(url),
            "cached_at": datetime.now().isoformat(),
            "data": data,
        }

        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            pass

    def clear(self, endpoint: str = None) -> None:
        """Clear cache - optionally for specific endpoint."""
        cleared = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    cache_data = json.load(f)

                if endpoint is None or cache_data.get("endpoint") == endpoint:
                    cache_file.unlink()
                    cleared += 1
            except Exception:
                cache_file.unlink()

        print(
            f"{Color.GREEN}✓ Cleared {cleared} cache entries"
            + (f" for endpoint '{endpoint}'" if endpoint else "")
            + f"{Color.RESET}"
        )

    def stats(self) -> dict:
        """Get cache statistics."""
        stats = {
            "total": 0,
            "by_endpoint": {},
            "oldest": None,
            "newest": None,
            "total_size": 0,
        }

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    cache_data = json.load(f)

                stats["total"] += 1
                stats["total_size"] += cache_file.stat().st_size

                endpoint = cache_data.get("endpoint", "unknown")
                stats["by_endpoint"][endpoint] = (
                    stats["by_endpoint"].get(endpoint, 0) + 1
                )

                cached_time = datetime.fromisoformat(cache_data["cached_at"])
                if stats["oldest"] is None or cached_time < stats["oldest"]:
                    stats["oldest"] = cached_time
                if stats["newest"] is None or cached_time > stats["newest"]:
                    stats["newest"] = cached_time

            except Exception:
                continue

        return stats


