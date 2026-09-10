from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    name_category: str
    name_description: Optional[str] = None