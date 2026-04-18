from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "minimal"
    num_images: int = Field(default=1, ge=1, le=4)
    seed: Optional[int] = None


class GenerateResponse(BaseModel):
    images: List[str]  # base64-encoded PNG strings