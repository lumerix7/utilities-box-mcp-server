from typing import Annotated

from pydantic import Field, BaseModel


class GenerateUUIDResult(BaseModel):
    """Result of UUIDs generation."""

    uuids: Annotated[list[str], Field(description="Generated UUIDs.")]
