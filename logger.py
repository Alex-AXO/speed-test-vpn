try:
    from loguru import logger  # type: ignore
except Exception:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("speed-test-vpn")

    def catch(func=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logger.exception("Exception in %s", func.__name__)
            return wrapper
        if callable(func):
            return decorator(func)
        return decorator

    def add(*args, **kwargs):
        return None

    logger.catch = catch  # type: ignore
    logger.add = add  # type: ignore
