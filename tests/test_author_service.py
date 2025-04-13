import pytest
from app.schemas import Author


def test_create_author(author_service):
    author = author_service.create_author("Test Author", "Test Bio")
    assert isinstance(author, Author)
    assert author.name == "Test Author"
    assert author.bio == "Test Bio"


def test_get_all_authors(author_service):
    # Create test authors
    author_service.create_author("Author 1")
    author_service.create_author("Author 2")

    authors = author_service.get_all_authors()
    assert len(authors) == 2
    assert all(isinstance(author, Author) for author in authors)
    assert {author.name for author in authors} == {"Author 1", "Author 2"}


def test_get_author(author_service):
    created_author = author_service.create_author("Test Author")
    retrieved_author = author_service.get_author(created_author.id)

    assert isinstance(retrieved_author, Author)
    assert retrieved_author.id == created_author.id
    assert retrieved_author.name == "Test Author"


def test_get_nonexistent_author(author_service):
    with pytest.raises(Exception) as exc_info:
        author_service.get_author(999)
    assert "Author not found" in str(exc_info.value)
