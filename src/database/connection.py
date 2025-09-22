"""
Database connection management for PostgreSQL.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator, Dict, Any, List, Optional
from loguru import logger

from src.config.settings import db_settings


class DatabaseConnection:
    """Handles database connections and operations."""
    
    def __init__(self):
        self.connection_string = db_settings.connection_string
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine and session factory."""
        try:
            self.engine = create_engine(
                self.connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """Get a raw psycopg2 connection with context manager."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_settings.host,
                port=db_settings.port,
                database=db_settings.name,
                user=db_settings.user,
                password=db_settings.password,
                cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_session(self):
        """Get SQLAlchemy session with context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Database connection test successful")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise


# Global database connection instance
db_connection = DatabaseConnection()
