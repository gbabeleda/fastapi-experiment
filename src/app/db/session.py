"""
Database session management.

This module defines how the app connects to and interacts with the database,
using SQLAlchemys async engine and session system.

Design notes:
- Uses a single global async engine (connection pool manager)
- Session factory (`AsyncSessionLocal`) creates lightweight DB sessions on demand
- Sessions are closed automatically via context manager (`async with`)
- Transactions are **committed manually** in business logic (not here)
- Rolls back automatically if any exception occurs

Why manual commit?
------------------
It keeps transaction control inside your business logic.
Example:
    db.add(User(name="Gio"))
    await db.commit()
If anything fails before commit, we can handle partial logic cleanly.

Why expire_on_commit=False?
---------------------------
SQLAlchemy normally "expires" objects after commit,
forcing re-fetch from DB next time they're accessed.
That's fine in sync apps, but annoying in async where re-fetch
needs awaits. Disabling it makes the ORM object usable after commit.

Why autoflush=False?
--------------------
Autoflush automatically writes pending changes before queries.
Thats convenient but can cause unexpected I/O in async.
We keep full control with manual flush() or commit().
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Create async engine with connection pool manager
engine = create_async_engine(
    url=str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,  # Log SQL queries for debugging
    pool_size=settings.DB_POOL_SIZE,  # Steady-state pool size
    max_overflow=settings.DB_MAX_OVERFLOW,  # Allow temporary overflow connections
    future=True,
)

# Create session factory
# Each request gets its own session via this factory.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Dont expire objects after commit
    autoflush=False,  # Explicit control on when to flush
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a scoped async database session for each request.

    Usage (inside FastAPI route):
        @router.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()

    Notes:
    - Opens a new session per request (via context manager)
    - Closes it automatically when request ends
    - Rolls back if an exception occurs
    - Manual commit is expected inside business logic
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()  # Rollback on any error
            raise
