from typing import Annotated

from pydantic import Field, BaseModel


class GenerateUUIDResult(BaseModel):
    """Generate UUID result.

    Properties:
        - uuids: The generated UUIDs.
    """

    uuids: Annotated[list[str], Field(description="The generated UUIDs.")]
