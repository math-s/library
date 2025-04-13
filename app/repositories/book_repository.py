from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Book
from typing import List, Tuple

class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, isbn: str, author_id: int) -> Book:
        db_book = Book(title=title, isbn=isbn, author_id=author_id)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def get_all(self, skip: int = 0, limit: int = 10) -> Tuple[List[Book], int]:
        # Get total count
        total = self.db.query(Book).count()
        
        # Get paginated results
        books = (
            self.db.query(Book)
            .order_by(desc(Book.id))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return books, total

    def get_by_id(self, book_id: int) -> Book:
        return self.db.query(Book).filter(Book.id == book_id).first() 