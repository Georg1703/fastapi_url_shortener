import random
import string

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import get_first_link
from .schemas import ShortCodeAlias


def generate_alphanum_code() -> ShortCodeAlias:
    """Generates a random alphanumeric code"""

    return "".join(random.choices(string.ascii_letters + string.digits + '_', k=6))


async def get_non_existing_shortcode(db_session: AsyncSession) -> ShortCodeAlias:
    """Returns shortcode that does not exist in the database"""

    while True:
        shortcode = generate_alphanum_code()
        if not await get_first_link(db_session, {'short_url': shortcode}):
            return shortcode