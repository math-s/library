import pytest
from app.schemas import Book, PaginatedResponse, GoogleBook
from unittest.mock import AsyncMock, patch

# Mock response data
MOCK_GOOGLE_BOOKS_RESPONSE = {
    "items": [
        {
            "id": "test_id_1",
            "volumeInfo": {
                "title": "Test Book 1",
                "authors": ["Test Author 1"],
                "description": "Test Description 1",
                "industryIdentifiers": [
                    {"type": "ISBN_10", "identifier": "1234567890"}
                ],
                "publishedDate": "2023-01-01",
                "publisher": "Test Publisher",
            },
        },
        {
            "id": "test_id_2",
            "volumeInfo": {
                "title": "Test Book 2",
                "authors": ["Test Author 2"],
                "description": "Test Description 2",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9781234567890"}
                ],
                "publishedDate": "2023-02-01",
                "publisher": "Test Publisher",
            },
        },
    ]
}


@pytest.fixture
def mock_google_books_repository():
    with patch(
        "app.repositories.google_books_repository.GoogleBooksRepository"
    ) as mock:
        mock_instance = mock.return_value
        mock_instance.search_books = AsyncMock(
            return_value=[
                GoogleBook(
                    id="test_id_1",
                    title="Test Book 1",
                    authors=["Test Author 1"],
                    description="Test Description 1",
                    isbn="1234567890",
                    published_date="2023-01-01",
                    publisher="Test Publisher",
                ),
                GoogleBook(
                    id="test_id_2",
                    title="Test Book 2",
                    authors=["Test Author 2"],
                    description="Test Description 2",
                    isbn="9781234567890",
                    published_date="2023-02-01",
                    publisher="Test Publisher",
                ),
            ]
        )
        mock_instance.get_book_by_isbn = AsyncMock(
            return_value=GoogleBook(
                id="test_id_1",
                title="Test Book 1",
                authors=["Test Author 1"],
                description="Test Description 1",
                isbn="1234567890",
                published_date="2023-01-01",
                publisher="Test Publisher",
            )
        )
        mock_instance.get_books_by_author = AsyncMock(
            return_value=[
                GoogleBook(
                    id="test_id_1",
                    title="Test Book 1",
                    authors=["Test Author 1"],
                    description="Test Description 1",
                    isbn="1234567890",
                    published_date="2023-01-01",
                    publisher="Test Publisher",
                ),
                GoogleBook(
                    id="test_id_2",
                    title="Test Book 2",
                    authors=["Test Author 2"],
                    description="Test Description 2",
                    isbn="9781234567890",
                    published_date="2023-02-01",
                    publisher="Test Publisher",
                ),
            ]
        )
        yield mock_instance


@pytest.mark.asyncio
async def test_create_book(book_service, author_service):
    # First create an author
    author = author_service.create_author("Test Author")

    # Then create a book
    book = await book_service.create_book("Test Book", "1234567890", author.id)
    assert isinstance(book, Book)
    assert book.title == "Test Book"
    assert book.isbn == "1234567890"
    assert book.author_id == author.id


@pytest.mark.asyncio
async def test_create_book_nonexistent_author(book_service):
    with pytest.raises(Exception) as exc_info:
        await book_service.create_book("Test Book", "1234567890", 999)
    assert "Author not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_books(book_service, author_service):
    # Create test data
    author = author_service.create_author("Test Author")
    await book_service.create_book("Book 1", "1234567890", author.id)
    await book_service.create_book("Book 2", "0987654321", author.id)

    # Test pagination
    result = book_service.get_all_books(page=1, size=2)
    assert isinstance(result, PaginatedResponse)
    assert len(result.items) == 2
    assert result.total == 2
    assert result.page == 1
    assert result.size == 2
    assert result.pages == 1


@pytest.mark.asyncio
async def test_get_book(book_service, author_service):
    # Create test data
    author = author_service.create_author("Test Author")
    created_book = await book_service.create_book("Test Book", "1234567890", author.id)

    # Retrieve the book
    retrieved_book = book_service.get_book(created_book.id)
    assert isinstance(retrieved_book, Book)
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "Test Book"


def test_get_nonexistent_book(book_service):
    with pytest.raises(Exception) as exc_info:
        book_service.get_book(999)
    assert "Book not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_google_books(book_service, mock_google_books_repository):
    books = await book_service.search_google_books("python programming")
    assert isinstance(books, list)
    assert len(books) == 2
    assert books[0].title == "Test Book 1"
    assert books[1].title == "Test Book 2"
    mock_google_books_repository.search_books.assert_called_once_with(
        "python programming", 10
    )


@pytest.mark.asyncio
async def test_get_books_by_author_from_google(
    book_service, mock_google_books_repository
):
    books = await book_service.get_books_by_author_from_google("Test Author")
    assert isinstance(books, list)
    assert len(books) == 2
    assert books[0].authors[0] == "Test Author 1"
    assert books[1].authors[0] == "Test Author 2"
    mock_google_books_repository.get_books_by_author.assert_called_once_with(
        "Test Author", 10
    )
