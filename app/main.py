from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from typing import List, AsyncGenerator
from .repositories.author_repository import AuthorRepository
from .repositories.book_repository import BookRepository
from .repositories.google_books_repository import GoogleBooksRepository, GoogleBook
from .services.author_service import AuthorService
from .services.book_service import BookService
from .schemas import (
    AuthorCreate, Author, BookCreate, Book, PaginatedResponse,
    GoogleBook as GoogleBookSchema
)
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")

# Dependency injection for repositories
def get_author_repository(db: Session = Depends(get_db)) -> AuthorRepository:
    return AuthorRepository(db)

def get_book_repository(db: Session = Depends(get_db)) -> BookRepository:
    return BookRepository(db)

async def get_google_books_repository() -> AsyncGenerator[GoogleBooksRepository, None]:
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_BOOKS_API_KEY environment variable is not set")
    repository = GoogleBooksRepository(api_key)
    try:
        yield repository
    finally:
        await repository.close()

# Dependency injection for services
def get_author_service(author_repository: AuthorRepository = Depends(get_author_repository)) -> AuthorService:
    return AuthorService(author_repository)

async def get_book_service(
    book_repository: BookRepository = Depends(get_book_repository),
    author_repository: AuthorRepository = Depends(get_author_repository),
    google_books_repository: GoogleBooksRepository = Depends(get_google_books_repository)
) -> BookService:
    return BookService(book_repository, author_repository, google_books_repository)

@app.get("/")
async def root():
    return {"message": "Welcome to the Library Management System"}

# Author endpoints
@app.post("/authors/", response_model=Author)
async def create_author(
    author: AuthorCreate,
    author_service: AuthorService = Depends(get_author_service)
):
    return author_service.create_author(author.name, author.bio)

@app.get("/authors/", response_model=List[Author])
async def get_authors(author_service: AuthorService = Depends(get_author_service)):
    return author_service.get_all_authors()

@app.get("/authors/{author_id}", response_model=Author)
async def get_author(author_id: int, author_service: AuthorService = Depends(get_author_service)):
    return author_service.get_author(author_id)

# Book endpoints
@app.post("/books/", response_model=Book)
async def create_book(
    book: BookCreate,
    book_service: BookService = Depends(get_book_service)
):
    return await book_service.create_book(book.title, book.isbn, book.author_id)

@app.get("/books/", response_model=PaginatedResponse)
async def get_books(
    page: int = 1,
    size: int = 10,
    book_service: BookService = Depends(get_book_service)
):
    result = book_service.get_all_books(page=page, size=size)
    return {
        "items": result["items"],
        "total": result["total"],
        "page": result["page"],
        "size": result["size"],
        "pages": result["pages"]
    }

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, book_service: BookService = Depends(get_book_service)):
    return book_service.get_book(book_id)

# Google Books API endpoints
@app.get("/google-books/search", response_model=List[GoogleBookSchema])
async def search_google_books(
    query: str,
    max_results: int = 10,
    book_service: BookService = Depends(get_book_service)
):
    return await book_service.search_google_books(query, max_results)

@app.get("/google-books/author/{author_name}", response_model=List[GoogleBookSchema])
async def get_books_by_author(
    author_name: str,
    max_results: int = 10,
    book_service: BookService = Depends(get_book_service)
):
    return await book_service.get_books_by_author_from_google(author_name, max_results) 