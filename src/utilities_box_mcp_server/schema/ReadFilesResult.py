from typing import Annotated

from pydantic import Field, BaseModel


class FileContent(BaseModel):
    file_path: Annotated[str, Field(description="Path to the file that was read.")]
    content: Annotated[str, Field(description="Content of the file, in utf-8 encoding.")]


class ReadFilesResult(BaseModel):
    content_list: Annotated[list[FileContent], Field(description="Contents of the files that were read.")]
