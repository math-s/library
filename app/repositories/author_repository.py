from sqlalchemy.orm import Session
from ..models import Author


class AuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, bio: str = None) -> Author:
        db_author = Author(name=name, bio=bio)
        self.db.add(db_author)
        self.db.commit()
        self.db.refresh(db_author)
        return db_author

    def get_all(self) -> list[Author]:
        return self.db.query(Author).all()

    def get_by_id(self, author_id: int) -> Author:
        return self.db.query(Author).filter(Author.id == author_id).first()
