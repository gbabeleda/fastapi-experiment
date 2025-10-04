from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All database tables inherit from this.
    Provides shared functionality and metadata tracking.
    """

    pass
