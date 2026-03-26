from abc import ABC, abstractmethod
from typing import AsyncGenerator
from models.product import Product
import asyncio

class BaseScraperDetails(ABC):

    def __init__(self, concurrency: int = 10) -> None:
        self.sem = asyncio.Semaphore(concurrency)

    @abstractmethod
    async def fetch_product_details(self, products: list[Product]) -> AsyncGenerator[Product, None]: ...
