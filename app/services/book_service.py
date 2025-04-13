from fastapi import HTTPException
from ..repositories.book_repository import BookRepository
from ..repositories.author_repository import AuthorRepository
from ..repositories.google_books_repository import GoogleBooksRepository, GoogleBook
from ..models import Book
from ..schemas import Book as BookSchema, PaginatedResponse
from typing import List, Optional, Dict


class BookService:
    def __init__(
        self,
        book_repository: BookRepository,
        author_repository: AuthorRepository,
        google_books_repository: GoogleBooksRepository,
    ):
        self.book_repository = book_repository
        self.author_repository = author_repository
        self.google_books_repository = google_books_repository

    async def create_book(self, title: str, isbn: str, author_id: int) -> BookSchema:
        # Check if author exists
        author = self.author_repository.get_by_id(author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        # Try to get additional book information from Google Books
        google_book = await self.google_books_repository.get_book_by_isbn(isbn)

        db_book = self.book_repository.create(title, isbn, author_id)
        return BookSchema.model_validate(db_book)

    def get_all_books(self, page: int = 1, size: int = 10) -> PaginatedResponse:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be greater than 0")
        if size < 1:
            raise HTTPException(status_code=400, detail="Size must be greater than 0")

        skip = (page - 1) * size
        books, total = self.book_repository.get_all(skip=skip, limit=size)

        return PaginatedResponse(
            items=[BookSchema.model_validate(book) for book in books],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )

    def get_book(self, book_id: int) -> BookSchema:
        book = self.book_repository.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return BookSchema.model_validate(book)

    async def search_google_books(
        self, query: str, max_results: int = 10
    ) -> List[GoogleBook]:
        return await self.google_books_repository.search_books(query, max_results)

    async def get_books_by_author_from_google(
        self, author_name: str, max_results: int = 10
    ) -> List[GoogleBook]:
        return await self.google_books_repository.get_books_by_author(
            author_name, max_results
        )
