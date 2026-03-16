from abc import ABC, abstractmethod
from typing import AsyncGenerator
from models.product import Product

class BaseScraper(ABC):


    @abstractmethod
    async def fetch_products(self) -> AsyncGenerator[Product, None]: ...
