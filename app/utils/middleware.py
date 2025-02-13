from fastapi import Request  # type: ignore
from utils.logger import logger
from datetime import datetime
import time


async def middleware_log(request: Request, call_next):
    """
    Middleware function that logs information about the incoming request
    and the corresponding response.

    Args:
        request (Request): The incoming request object.
        call_next (Callable): The next middleware or endpoint to call.

    Returns:
        Response: The response object returned by the next middleware
        or endpoint.
    """
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "duration": duration,
    }
    logger.info(log_dict, extra=log_dict)
    return response
