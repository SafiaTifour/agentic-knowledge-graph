import asyncio
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

def async_retry_with_fallback(max_retries: int = 3, base_delay: float = 1.0, fallback_value: Any = None):
    """
    Decorator that retries an async function upon failure with exponential backoff.
    If it fails more than max_retries, it will return the fallback_value.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed in {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"All {max_retries} attempts failed in {func.__name__}. Using fallback.")
                        break
                    await asyncio.sleep(delay)
                    delay *= 2
            
            # If we land here, all retries failed
            return fallback_value
        return wrapper
    return decorator
