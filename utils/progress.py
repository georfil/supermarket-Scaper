import asyncio
import functools
import inspect
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def track(desc: str = None, unit: str = "item"):
    """
    Decorator that logs start, completion, count, elapsed time, and errors.
    Works on async generators, async functions, and sync functions.
    """
    def decorator(func):
        label = desc or func.__name__
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        async def async_gen_wrapper(self, *args, **kwargs):
            logger.info(f"{label} — started")
            count = 0
            start = time.perf_counter()
            try:
                async for item in func(self, *args, **kwargs):
                    count += 1
                    yield item
                logger.info(f"{label} — done ({count} {unit}s in {time.perf_counter() - start:.1f}s)")
            except Exception as e:
                logger.error(f"{label} — failed after {count} {unit}s: {e}")
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"{label} — started")
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                logger.info(f"{label} — done ({time.perf_counter() - start:.1f}s)")
                return result
            except Exception as e:
                logger.error(f"{label} — failed: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.info(f"{label} — started")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                logger.info(f"{label} — done ({time.perf_counter() - start:.1f}s)")
                return result
            except Exception as e:
                logger.error(f"{label} — failed: {e}")
                raise

        if inspect.isasyncgenfunction(func):
            return async_gen_wrapper
        elif asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
