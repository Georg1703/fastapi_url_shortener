from sqlalchemy import select

from src.url_shortner.comtrollers import generate_alphanum_code, get_non_existing_shortcode
from src.url_shortner.models import Link

def test_generate_alphanum_code():
    shortcode = generate_alphanum_code()

    expected_len = 6
    if '_' in shortcode:
        expected_len = 5
        shortcode = shortcode.replace('_', '')

    assert shortcode.isalnum()
    assert len(shortcode) == expected_len


async def test_get_non_existing_shortcode(session, populate_link_table):
    shortcode = await get_non_existing_shortcode(session)
    link = await session.execute(select(Link).filter_by(shortcode=shortcode))
    assert link.first() is None