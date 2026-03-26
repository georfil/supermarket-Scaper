import asyncio
import logging
import aiohttp
from typing import Any

logger = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=30)
_MAX_RETRIES = 3


async def _fetch(session: aiohttp.ClientSession, url: str, mode: str, **kwargs) -> Any:
    for attempt in range(_MAX_RETRIES):
        try:
            async with session.get(url, timeout=_TIMEOUT, **kwargs) as response:
                response.raise_for_status()
                if mode == "json":
                    return await response.json()
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if isinstance(e, aiohttp.ClientResponseError) and e.status < 500:
                if e.status != 404:
                    logger.error("Non-retryable error for %s (status %d): %s", url, e.status, e)
                raise
            if attempt == _MAX_RETRIES - 1:
                logger.error("Request to %s failed after %d attempts: %s", url, _MAX_RETRIES, e)
                raise
            wait = 2.0 ** attempt
            logger.warning(
                "Request to %s failed (attempt %d/%d), retrying in %.1fs: %s",
                url, attempt + 1, _MAX_RETRIES, wait, e
            )
            await asyncio.sleep(wait)


async def fetch_json(session: aiohttp.ClientSession, url: str, **kwargs) -> Any:
    return await _fetch(session, url, "json", **kwargs)


async def fetch_text(session: aiohttp.ClientSession, url: str, **kwargs) -> str:
    return await _fetch(session, url, "text", **kwargs)
