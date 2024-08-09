from typing import Union
from pydantic import *


class Link(BaseModel):
    url: str
    password: Union[str, None] = None


class LinkDonate(BaseModel):
    url: str


class LinkQRCODE(BaseModel):
    data: str
    version: Union[int, None] = 1
    error_correction: Union[int, None] = 0
    box_size: Union[int, None] = 10
    border: Union[int, None] = 4
    mask_pattern: Union[int, None] = 0


class Password(BaseModel):
    password: Union[str, None] = None

# 코체 멍청이
