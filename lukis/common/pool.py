from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Generic, Optional, TypeVar

__all__ = "ConnectionPool", "ConnectionStrategy"
Conn = TypeVar("Conn")


class ConnectionStrategy(ABC, Generic[Conn]):
    @abstractmethod
    async def make_connection(self) -> Awaitable[Conn]:
        ...

    @abstractmethod
    def connection_is_closed(self, conn: Conn) -> bool:
        ...

    @abstractmethod
    async def close_connection(self, conn: Conn) -> None:
        ...


class ConnectionPool(Generic[Conn]):
    def __init__(
        self,
        strategy: ConnectionStrategy[Conn],
        max_size: int,
        burst_limit: Optional[int] = None,
    ):
        self.strategy = strategy
        self.max_size = max_size
        self.burst_limit = burst_limit
        if burst_limit is not None and burst_limit < max_size:
            raise ValueError("burst_limit must be greater than or equal to max_size")
        self.in_use = 0
        self.currently_allocating = 0
        self.currently_deallocating = 0
        self._loop = self._available = None

    @property
    def loop(self):
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return self._loop

    @property
    def available(self):
        if self._available is None:
            self._available = asyncio.Queue(maxsize=self.max_size)
        return self._available

    @property
    def total(self) -> int:
        return self.in_use + self.currently_allocating + self.available.qsize()

    @property
    def _waiters(self):
        waiters = self.available._getters
        return sum(not (w.done() or w.cancelled()) for w in waiters)

    async def _connection_maker(self):
        try:
            conn = await self.strategy.make_connection()
        finally:
            self.currently_allocating -= 1
        self.in_use += 1
        return conn

    async def _connection_waiter(self):
        conn = await self.available.get()
        self.in_use += 1
        return conn

    def _get_conn(self) -> "Awaitable[Conn]":
        if not self.available.empty():
            fut: "asyncio.Future[Conn]" = self.loop.create_future()
            fut.set_result(self.available.get_nowait())
            self.in_use += 1
            return fut
        elif self.total < self.max_size or (
            self.burst_limit is not None and self.total < self.burst_limit
        ):
            self.currently_allocating += 1
            return self.loop.create_task(self._connection_maker())
        else:
            return self._loop.create_task(self._connection_waiter())

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[Conn]:
        conn = await self._get_conn()
        while True:
            try:
                if not self.strategy.connection_is_closed(conn):
                    break
            except BaseException:
                self.in_use -= 1
                raise
            self.in_use -= 1
            conn = await self._get_conn()

        try:
            yield conn
        finally:
            self.currently_deallocating += 1
            try:
                if (
                    self.total - self.currently_deallocating >= self.max_size
                    and self._waiters == 0
                ):
                    await self.strategy.close_connection(conn)
                else:
                    try:
                        self.available.put_nowait(conn)
                    except asyncio.QueueFull:
                        await self.strategy.close_connection(conn)
            finally:
                self.currently_deallocating -= 1
                self.in_use -= 1
                assert self.in_use >= 0, "More connections returned than given"
