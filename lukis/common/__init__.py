from .pool import ConnectionPool, ConnectionStrategy
from .chrome import PyppeteerStrategy
from ..config import CHROME_WEBSOCKET


chrome_pool = ConnectionPool(
    strategy=PyppeteerStrategy(CHROME_WEBSOCKET),
    max_size=7,
    burst_limit=10,
)
