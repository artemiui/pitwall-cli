"""HTTP client with retry logic and caching."""

from typing import Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .colors import Color
from .state import f1_cache


def fetch_json(url: str, force_refresh: bool = False) -> Dict:
    """Fetch JSON from URL with caching and retry logic."""
    if not force_refresh:
        cached_data = f1_cache.get(url)
        if cached_data is not None:
            return cached_data

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=1,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    timeout_config = (3.0, 10.0)

    try:
        response = session.get(url, timeout=timeout_config)
        response.raise_for_status()
        data = response.json()

        f1_cache.set(url, data)
        return data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"{Color.RED}✗ Rate limit hit. Please slow down requests.{Color.RESET}")
        else:
            print(f"{Color.RED}✗ HTTP error {e.response.status_code}: {e}{Color.RESET}")
        return None
    except requests.exceptions.Timeout:
        print(f"{Color.YELLOW}⚠ Request timed out after multiple attempts.{Color.RESET}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Color.RED}✗ Network error: {e}{Color.RESET}")
        return None


