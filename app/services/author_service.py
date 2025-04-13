from fastapi import HTTPException
from ..repositories.author_repository import AuthorRepository
from ..models import Author
from ..schemas import Author as AuthorSchema
from typing import List


class AuthorService:
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    def create_author(self, name: str, bio: str = None) -> AuthorSchema:
        db_author = self.author_repository.create(name, bio)
        return AuthorSchema.model_validate(db_author)

    def get_all_authors(self) -> List[AuthorSchema]:
        authors = self.author_repository.get_all()
        return [AuthorSchema.model_validate(author) for author in authors]

    def get_author(self, author_id: int) -> AuthorSchema:
        author = self.author_repository.get_by_id(author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")
        return AuthorSchema.model_validate(author)
