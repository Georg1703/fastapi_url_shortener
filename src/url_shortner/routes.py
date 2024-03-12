from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from .comtrollers import get_non_existing_shortcode
from . import repository
from . import schemas

router = APIRouter()


@router.post("/shorten", response_model=schemas.ShortLinkResponse, status_code=status.HTTP_201_CREATED)
async def ger_or_create_shortcode(data: schemas.ShortLinkRequest, response: Response, db_session: AsyncSession = Depends(get_session)):
    """Returns a shortcode for the provided url"""

    if existing_link := await repository.get_first_link(db_session, {"original_url": str(data.url)}):
        await repository.update_link(db_session, existing_link)
        response.status_code = status.HTTP_200_OK
        return schemas.ShortLinkResponse(shortcode=existing_link.shortcode)
    
    if data.shortcode:
        try:
            await repository.save_new_link(db_session, data.url, data.shortcode)
            return schemas.ShortLinkResponse(shortcode=data.shortcode)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Shortcode already in use")
        
    shortcode = await get_non_existing_shortcode(db_session)
    await repository.save_new_link(db_session, data.url, shortcode)
    return schemas.ShortLinkResponse(shortcode=shortcode)


@router.get("/{shortcode}", status_code=status.HTTP_302_FOUND)
async def get_original_url(shortcode: schemas.ShortCodeAlias, response: Response, db_session: AsyncSession = Depends(get_session)):
    """Set Location header to original url by shortcode"""

    if existing_link := await repository.get_first_link(db_session, {"shortcode": shortcode}):
        await repository.update_link(db_session, existing_link)
        response.headers["Location"] = existing_link.original_url
        return
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortcode not found")


@router.get("/{shortcode}/stats", status_code=status.HTTP_200_OK)
async def get_shortcode_statistic(shortcode: schemas.ShortCodeAlias, db_session: AsyncSession = Depends(get_session)):
    """Returns statistics for the provided shortcode"""

    if existing_link := await repository.get_first_link(db_session, {"shortcode": shortcode}):
        return schemas.ShortcodeStatsResponse(
            created=existing_link.created_at.isoformat(),
            last_redirected=existing_link.last_redirected_at.isoformat(),
            redirect_count=existing_link.redirects_count
        )
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortcode not found")