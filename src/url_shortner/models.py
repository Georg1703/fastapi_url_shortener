import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    original_url: Mapped[str] = mapped_column(index=True, unique=True)
    shortcode: Mapped[str] = mapped_column(index=True, unique=True)
    redirects_count: Mapped[int] = mapped_column(default=0)
    last_redirected_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )