from typing import Annotated
from pydantic import BaseModel, UrlConstraints, AnyUrl
from pydantic.types import StringConstraints


ShortCodeAlias = Annotated[str, StringConstraints(min_length=6, max_length=6, pattern=r'^[a-zA-Z0-9_]+$')]
UrlAlias = Annotated[AnyUrl, UrlConstraints(allowed_schemes=["http", "https"])]


class ShortLinkRequest(BaseModel):
    url: UrlAlias
    shortcode: ShortCodeAlias = None


class ShortLinkResponse(BaseModel):
    shortcode: ShortCodeAlias


class ShortcodeStatsResponse(BaseModel):
    created: str
    last_redirected: str
    redirect_count: int
