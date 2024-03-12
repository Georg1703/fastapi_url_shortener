from datetime import datetime
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UrlAlias, ShortCodeAlias
from .models import Link


async def save_new_link(db_session: AsyncSession, original_url: UrlAlias, shortcode: ShortCodeAlias) -> ShortCodeAlias:
    """Saves a new link to the database"""

    new_link = Link(
        original_url=str(original_url),
        shortcode=shortcode,
        last_redirected_at=datetime.now(timezone.utc)
    )
    db_session.add(new_link)
    await db_session.commit()
    return shortcode


async def get_first_link(db_session: AsyncSession, params: dict) -> Link:
    """Returns the first link that match criteria from the database"""

    query = select(Link).filter_by(**params)
    result = await db_session.execute(query)
    return result.scalars().first()


async def update_link(db_session: AsyncSession, link: Link) -> None:
    """Updates the link in the database"""
    
    link.redirects_count += 1
    link.last_redirected_at = datetime.now(timezone.utc)
    await db_session.commit()