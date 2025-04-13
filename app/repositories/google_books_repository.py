from typing import Optional, List, Dict
import httpx
from pydantic import BaseModel

class GoogleBook(BaseModel):
    id: str
    title: str
    authors: List[str]
    description: Optional[str]
    isbn: Optional[str]
    published_date: Optional[str]
    publisher: Optional[str]

class GoogleBooksRepository:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    async def search_books(self, query: str, max_results: int = 10) -> List[GoogleBook]:
        params = {
            "q": query,
            "maxResults": max_results,
            "key": self.api_key
        }
        
        response = await self.client.get(f"{self.BASE_URL}", params=params)
        response.raise_for_status()
        
        books_data = response.json()
        books = []
        
        for item in books_data.get("items", []):
            volume_info = item["volumeInfo"]
            book = GoogleBook(
                id=item["id"],
                title=volume_info.get("title", ""),
                authors=volume_info.get("authors", []),
                description=volume_info.get("description"),
                isbn=self._extract_isbn(volume_info.get("industryIdentifiers", [])),
                published_date=volume_info.get("publishedDate"),
                publisher=volume_info.get("publisher")
            )
            books.append(book)
        
        return books

    async def get_book_by_isbn(self, isbn: str) -> Optional[GoogleBook]:
        query = f"isbn:{isbn}"
        books = await self.search_books(query, max_results=1)
        return books[0] if books else None

    async def get_books_by_author(self, author_name: str, max_results: int = 10) -> List[GoogleBook]:
        query = f"inauthor:{author_name}"
        return await self.search_books(query, max_results)

    def _extract_isbn(self, identifiers: List[Dict[str, str]]) -> Optional[str]:
        for identifier in identifiers:
            if identifier.get("type") in ["ISBN_10", "ISBN_13"]:
                return identifier.get("identifier")
        return None

    async def close(self):
        await self.client.aclose() 