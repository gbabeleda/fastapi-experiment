from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All database tables inherit from this.
    Provides shared functionality and metadata tracking.
    """

    pass


# Import all models so they register with Base.metadata
# This MUST happen after Base is defined
from app.db.models.ecommerce import *  # noqa: F403, E402
