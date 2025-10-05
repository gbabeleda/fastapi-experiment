"""
Ecommerce domain models.

All models live in the 'ecommerce' PostgreSQL schema.
Basic implementation focused on getting deployment working - can be enhanced later.

These models are designed to be easy to reason about and evolve incrementally
while maintaining compatibility with Alembic migrations.


This module defines the SQLAlchemy ORM models used in the FastAPI backend.
It intentionally uses **modern SQLAlchemy 2.0 style syntax**, e.g.:
    - `Mapped[...]` and `mapped_column()`
    - explicit `relationship()` definitions
    - type-hinted attributes for better editor support and static analysis

Simplifications:
    - Only core constraints (primary/foreign keys, uniqueness) are defined.
      More complex constraints (e.g., check constraints, on-delete cascades)
      can be added later once the schema stabilizes.
    - Table and column names are kept straightforward and descriptive
      rather than fully normalized.

Relationships:
    - User → Order (one-to-many)
    - Order → OrderItem (one-to-many)
    - OrderItem → Product (many-to-one)
    - User → Address (one-to-many)
    - Category → Product (one-to-many)

Because relationships are defined using `relationship()`, you can access related
data directly as attributes instead of writing explicit joins. For example:
    `order.user.email` or `user.orders[0].items`
SQLAlchemy will handle the necessary joins under the hood, keeping queries
intuitive and Pythonic.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    """User accounts for the ecommerce platform."""

    __tablename__ = "users"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")


class Category(Base, TimestampMixin):
    """Product categories."""

    __tablename__ = "categories"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    # Relationships
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base, TimestampMixin):
    """Products available for purchase."""

    __tablename__ = "products"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("ecommerce.categories.id"), nullable=True, index=True
    )

    # Relationships
    category: Mapped["Category | None"] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base, TimestampMixin):
    """Customer orders."""

    __tablename__ = "orders"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("ecommerce.users.id"), nullable=False, index=True
    )

    total: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="pending", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    """Line items within an order."""

    __tablename__ = "order_items"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("ecommerce.orders.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("ecommerce.products.id"), nullable=False, index=True
    )

    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class Address(Base, TimestampMixin):
    """User shipping and billing addresses."""

    __tablename__ = "addresses"
    __table_args__ = {"schema": "ecommerce"}

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("ecommerce.users.id"), nullable=False, index=True
    )

    street: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str | None] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=False)
    postal_code: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="addresses")
