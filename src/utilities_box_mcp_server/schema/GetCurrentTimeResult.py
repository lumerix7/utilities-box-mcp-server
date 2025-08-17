from typing import Annotated

from pydantic import Field, BaseModel


class GetCurrentTimeResult(BaseModel):
    datetime: Annotated[str, Field(description="Current time in a specified format.")]
    tz_name: Annotated[str, Field(description="Timezone name for the datetime, if available.")]
    tz_offset: Annotated[int | None, Field(
        description="Timezone offset as timedelta positive east of UTC (negative west of UTC) for the datetime, in seconds, if available.")]
