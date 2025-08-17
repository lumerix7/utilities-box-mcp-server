from typing import Annotated

from pydantic import Field, BaseModel


class ReadLinesResult(BaseModel):
    file_path: Annotated[str, Field(description="Path to the file that was read.")]
    begin_line: Annotated[int, Field(description="Line number where reading started (1-indexed).")]
    num_lines: Annotated[int, Field(description="Number of lines that were actually read.")]
    content_lines: Annotated[
        list[str], Field(description="Content lines of the file as a list of strings in utf-8 encoding.")]
