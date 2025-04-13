from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    isbn: str = Field(..., min_length=10, max_length=13, pattern=r'^[0-9-]+$')
    author_id: int = Field(..., gt=0)

class BookCreate(BookBase):
    pass

class BookAuthor(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class Book(BookBase):
    id: int
    author: BookAuthor
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int = Field(..., ge=0)
    page: int = Field(..., gt=0)
    size: int = Field(..., gt=0)
    pages: int = Field(..., ge=0)

class GoogleBook(BaseModel):
    id: str
    title: str
    authors: List[str]
    description: Optional[str]
    isbn: Optional[str]
    published_date: Optional[str]
    publisher: Optional[str] 