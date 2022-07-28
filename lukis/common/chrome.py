from .pool import ConnectionStrategy
from pyppeteer import connect as connect_browserless
from pyppeteer.browser import Browser


class PyppeteerStrategy(ConnectionStrategy[Browser]):
    def __init__(self, ws_endpoint: str):
        self.ws_endpoint = ws_endpoint

    async def make_connection(self):
        return await connect_browserless(
            options={"browserWSEndpoint": self.ws_endpoint}
        )

    def connection_is_closed(self, conn):
        return not conn._connection._connected

    async def close_connection(self, conn):
        await conn.close()
