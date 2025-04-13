import pytest
import docker
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database, database_exists
from app.database import Base, get_db
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.google_books_repository import GoogleBooksRepository
from app.services.author_service import AuthorService
from app.services.book_service import BookService

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/library_test"

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            engine = create_engine(TEST_DATABASE_URL)
            engine.connect()
            return True
        except Exception:
            retry_count += 1
            time.sleep(2)
    return False

@pytest.fixture(scope="session")
def docker_setup():
    """Setup and teardown Docker container"""
    client = docker.from_env()
    
    # Start the container
    container = client.containers.run(
        "postgres:15",
        environment={
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "library_test"
        },
        ports={'5432/tcp': 5433},
        detach=True
    )
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        container.stop()
        container.remove()
        raise Exception("Failed to start PostgreSQL container")
    
    yield
    
    # Cleanup
    container.stop()
    container.remove()

@pytest.fixture(scope="session")
def test_engine(docker_setup):
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)
    
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    drop_database(TEST_DATABASE_URL)

@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def author_repository(db_session):
    return AuthorRepository(db_session)

@pytest.fixture
def book_repository(db_session):
    return BookRepository(db_session)

@pytest.fixture
def google_books_repository():
    return GoogleBooksRepository("test_api_key")

@pytest.fixture
def author_service(author_repository):
    return AuthorService(author_repository)

@pytest.fixture
def book_service(book_repository, author_repository, mock_google_books_repository):
    return BookService(book_repository, author_repository, mock_google_books_repository) 